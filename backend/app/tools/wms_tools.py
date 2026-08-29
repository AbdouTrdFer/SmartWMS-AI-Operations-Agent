import logging
import re
from dataclasses import dataclass

from app.core.logging import safe_tool_log
from app.repositories.wms_repository import WMSRepository
from app.services.business_decisions import WMSBusinessDecisionService

logger = logging.getLogger(__name__)

SKU_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9-]{2,39}$")
WAREHOUSE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9-]{1,19}$")


@dataclass(frozen=True)
class ToolResult:
    name: str
    facts: list[str]


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


def _available(quantity: int, reserved_quantity: int) -> int:
    return quantity - reserved_quantity


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
            return ToolResult("get_inventory", [f"No inventory record found for {sku}."])
        open_orders = self.repository.get_open_orders(warehouse)
        facts = [
            self._format_inventory_position(
                self.decisions.build_inventory_position(row, open_orders)
            )
            for row in rows
        ]
        return ToolResult("get_inventory", facts)

    def get_low_stock_items(self, warehouse_code: str | None = None) -> ToolResult:
        safe_tool_log(logger, "get_low_stock_items")
        warehouse = _validate_warehouse(warehouse_code)
        rows = self.repository.get_inventory_positions(warehouse)
        open_orders = self.repository.get_open_orders(warehouse)
        positions = [
            self.decisions.build_inventory_position(row, open_orders)
            for row in rows
        ]
        low_stock_positions = [position for position in positions if position.is_low_stock]
        if not low_stock_positions:
            return ToolResult("get_low_stock_items", ["No low-stock items found."])
        facts = [
            self._format_reorder_position(position)
            for position in sorted(
                low_stock_positions,
                key=lambda item: (item.reorder_priority, item.available_quantity),
            )
        ]
        return ToolResult("get_low_stock_items", facts)

    def get_product(self, product_sku: str) -> ToolResult:
        safe_tool_log(logger, "get_product")
        sku = _validate_sku(product_sku)
        product = self.repository.get_product(sku)
        if not product:
            return ToolResult("get_product", [f"No product found for {sku}."])
        profile = self.decisions.build_product_profile(product)
        return ToolResult(
            "get_product",
            [
                (
                    f"{profile.sku} is {profile.name} in {profile.category}; reorder point "
                    f"{profile.reorder_point}, target stock {profile.target_stock}, supplier "
                    f"{profile.supplier_name}, lead time {profile.supplier_lead_time_days} days, "
                    f"reliability {profile.supplier_reliability_score:.2f}."
                )
            ],
        )

    def get_open_orders(self, warehouse_code: str | None = None) -> ToolResult:
        safe_tool_log(logger, "get_open_orders")
        warehouse = _validate_warehouse(warehouse_code)
        orders = self.repository.get_open_orders(warehouse)
        if not orders:
            return ToolResult("get_open_orders", ["No open orders found."])
        facts = []
        for order in orders:
            item_summary = ", ".join(
                f"{item.product.sku} x {item.quantity}"
                for item in sorted(order.items, key=lambda i: i.id)
            )
            facts.append(
                f"{order.customer_reference} at {order.warehouse.code}: priority {order.priority}, "
                f"items {item_summary}."
            )
        return ToolResult("get_open_orders", facts)

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
            )
        facts = [
            (
                f"{row.product.sku} {row.movement_type} at {row.warehouse.code}: "
                f"{row.quantity} units on {row.timestamp.date().isoformat()}."
            )
            for row in rows
        ]
        return ToolResult("get_stock_movements", facts)

    def _format_inventory_position(self, position) -> str:
        return (
            f"{position.sku} at {position.warehouse_code}: on-hand "
            f"{position.on_hand_quantity}, reserved {position.reserved_quantity}, "
            f"available {position.available_quantity}, open demand "
            f"{position.open_demand_quantity}, low stock {position.is_low_stock}, "
            f"stockout {position.is_stockout}."
        )

    def _format_reorder_position(self, position) -> str:
        reasons = ", ".join(position.reason_codes) if position.reason_codes else "NO_ACTION"
        return (
            f"{position.sku} at {position.warehouse_code}: available "
            f"{position.available_quantity} vs reorder point {position.reorder_point}; "
            f"open demand {position.open_demand_quantity}; stockout gap "
            f"{position.stockout_gap_quantity}; supplier lead time "
            f"{position.supplier_lead_time_days} days; reorder priority "
            f"{position.reorder_priority}; suggested reorder quantity "
            f"{position.suggested_reorder_quantity}; reasons {reasons}."
        )
