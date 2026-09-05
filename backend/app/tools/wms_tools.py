import logging
import re
from dataclasses import dataclass
from typing import Any

from app.core.logging import safe_tool_log
from app.repositories.wms_repository import WMSRepository
from app.services.business_decisions import ReplenishmentAnalysisResult, WMSBusinessDecisionService

logger = logging.getLogger(__name__)

SKU_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9-]{2,39}$")
WAREHOUSE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9-]{1,19}$")


@dataclass(frozen=True)
class ToolResult:
    name: str
    facts: list[str]
    records: list[dict[str, Any]]


def _validate_sku(product_sku: str) -> str:
    sku = product_sku.strip().upper()
    if not SKU_PATTERN.fullmatch(sku):
        raise ValueError("Invalid product_sku")
    return sku


def _validate_warehouse(warehouse_code: str | None) -> str | None:
    if warehouse_code is None:
        return None
    code = warehouse_code.strip().upper()
    if not WAREHOUSE_PATTERN.fullmatch(code):
        raise ValueError("Invalid warehouse_code")
    return code


class WMSTools:
    def __init__(self, repository: WMSRepository):
        self.repository = repository
        self.decisions = WMSBusinessDecisionService()

    def get_inventory(self, product_sku: str, warehouse_code: str | None = None) -> ToolResult:
        safe_tool_log(logger, "get_inventory")
        sku = _validate_sku(product_sku)
        warehouse = _validate_warehouse(warehouse_code)
        rows = self.repository.get_inventory(sku, warehouse)
        if not rows:
            return ToolResult("get_inventory", [f"No inventory record found for {sku}."], [])

        open_orders = self.repository.get_open_orders(warehouse)
        analyses = [
            self.decisions.build_replenishment_analysis(row, open_orders)
            for row in rows
        ]
        return ToolResult(
            name="get_inventory",
            facts=[self._format_inventory_analysis(analysis) for analysis in analyses],
            records=[analysis.to_dict() for analysis in analyses],
        )

    def get_low_stock_items(self, warehouse_code: str | None = None) -> ToolResult:
        safe_tool_log(logger, "get_low_stock_items")
        warehouse = _validate_warehouse(warehouse_code)
        rows = self.repository.get_inventory_positions(warehouse)
        open_orders = self.repository.get_open_orders(warehouse)
        analyses = [
            self.decisions.build_replenishment_analysis(row, open_orders)
            for row in rows
        ]
        low_stock_analyses = [
            analysis for analysis in analyses if analysis.low_stock_candidate
        ]
        if not low_stock_analyses:
            return ToolResult("get_low_stock_items", ["No low-stock items found."], [])

        ordered = sorted(
            low_stock_analyses,
            key=lambda item: (-item.replenishment_priority_score, item.available_quantity),
        )
        return ToolResult(
            name="get_low_stock_items",
            facts=[self._format_replenishment_analysis(analysis) for analysis in ordered],
            records=[analysis.to_dict() for analysis in ordered],
        )

    def get_product(self, product_sku: str) -> ToolResult:
        safe_tool_log(logger, "get_product")
        sku = _validate_sku(product_sku)
        product = self.repository.get_product(sku)
        if not product:
            return ToolResult("get_product", [f"No product found for {sku}."], [])

        profile = self.decisions.build_product_profile(product)
        return ToolResult(
            name="get_product",
            facts=[
                (
                    f"{profile.sku} is {profile.name} in {profile.category}; reorder point "
                    f"{profile.reorder_point}, target stock {profile.target_stock}, supplier "
                    f"{profile.supplier_name}, lead time {profile.supplier_lead_time_days} days, "
                    f"reliability {profile.supplier_reliability_score:.2f}."
                )
            ],
            records=[profile.to_dict()],
        )

    def get_open_orders(self, warehouse_code: str | None = None) -> ToolResult:
        safe_tool_log(logger, "get_open_orders")
        warehouse = _validate_warehouse(warehouse_code)
        orders = self.repository.get_open_orders(warehouse)
        if not orders:
            return ToolResult("get_open_orders", ["No open orders found."], [])

        facts = []
        records: list[dict[str, Any]] = []
        for order in orders:
            items = [
                {"sku": item.product.sku, "quantity": item.quantity}
                for item in sorted(order.items, key=lambda i: i.id)
            ]
            item_summary = ", ".join(
                f"{item['sku']} x {item['quantity']}"
                for item in items
            )
            facts.append(
                f"{order.customer_reference} at {order.warehouse.code}: priority {order.priority}, "
                f"items {item_summary}."
            )
            records.append(
                {
                    "customer_reference": order.customer_reference,
                    "warehouse_code": order.warehouse.code,
                    "status": order.status,
                    "priority": order.priority,
                    "items": items,
                }
            )
        return ToolResult("get_open_orders", facts, records)

    def get_stock_movements(self, product_sku: str, days: int) -> ToolResult:
        safe_tool_log(logger, "get_stock_movements")
        sku = _validate_sku(product_sku)
        if days < 1 or days > 90:
            raise ValueError("days must be between 1 and 90")
        rows = self.repository.get_stock_movements(sku, days)
        if not rows:
            return ToolResult(
                "get_stock_movements",
                [f"No movements found for {sku} in {days} days."],
                [],
            )

        facts = [
            (
                f"{row.product.sku} {row.movement_type} at {row.warehouse.code}: "
                f"{row.quantity} units on {row.timestamp.date().isoformat()}."
            )
            for row in rows
        ]
        records = [
            {
                "sku": row.product.sku,
                "warehouse_code": row.warehouse.code,
                "movement_type": row.movement_type,
                "quantity": row.quantity,
                "timestamp": row.timestamp.isoformat(),
            }
            for row in rows
        ]
        return ToolResult("get_stock_movements", facts, records)

    def _format_inventory_analysis(self, analysis: ReplenishmentAnalysisResult) -> str:
        return (
            f"{analysis.sku} at {analysis.warehouse_code}: on-hand "
            f"{analysis.on_hand_quantity}, reserved {analysis.reserved_quantity}, "
            f"inbound {analysis.inbound_quantity}, available "
            f"{analysis.available_quantity}, inventory position "
            f"{analysis.inventory_position}, open demand "
            f"{analysis.open_demand_quantity}, stockout risk {analysis.stockout_risk}."
        )

    def _format_replenishment_analysis(self, analysis: ReplenishmentAnalysisResult) -> str:
        reasons = ", ".join(analysis.reason_codes) if analysis.reason_codes else "NO_ACTION"
        return (
            f"{analysis.sku} at {analysis.warehouse_code}: low stock candidate "
            f"{analysis.low_stock_candidate}; available {analysis.available_quantity} "
            f"vs reorder point {analysis.reorder_point}; open demand "
            f"{analysis.open_demand_quantity}; demand shortfall "
            f"{analysis.demand_shortfall_quantity}; stockout risk {analysis.stockout_risk}; "
            f"replenishment candidate {analysis.replenishment_candidate}; priority score "
            f"{analysis.replenishment_priority_score}; priority band "
            f"{analysis.replenishment_priority_band}; reorder quantity "
            f"{analysis.reorder_quantity}; supplier lead time "
            f"{analysis.supplier_lead_time_days} days; reasons {reasons}."
        )
