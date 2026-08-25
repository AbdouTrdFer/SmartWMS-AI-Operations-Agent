import logging
import re
from dataclasses import dataclass

from app.core.logging import safe_tool_log
from app.repositories.wms_repository import WMSRepository

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

    def get_inventory(self, product_sku: str, warehouse_code: str | None = None) -> ToolResult:
        safe_tool_log(logger, "get_inventory")
        sku = _validate_sku(product_sku)
        warehouse = _validate_warehouse(warehouse_code)
        rows = self.repository.get_inventory(sku, warehouse)
        if not rows:
            return ToolResult("get_inventory", [f"No inventory record found for {sku}."])
        facts = [
            (
                f"{row.product.sku} at {row.warehouse.code}: on-hand {row.quantity}, "
                f"reserved {row.reserved_quantity}, available "
                f"{_available(row.quantity, row.reserved_quantity)}."
            )
            for row in rows
        ]
        return ToolResult("get_inventory", facts)

    def get_low_stock_items(self, warehouse_code: str | None = None) -> ToolResult:
        safe_tool_log(logger, "get_low_stock_items")
        warehouse = _validate_warehouse(warehouse_code)
        rows = self.repository.get_low_stock_items(warehouse)
        if not rows:
            return ToolResult("get_low_stock_items", ["No low-stock items found."])
        facts = [
            (
                f"{row.product.sku} at {row.warehouse.code}: available "
                f"{_available(row.quantity, row.reserved_quantity)} vs reorder point "
                f"{row.product.reorder_point}; supplier lead time "
                f"{row.product.supplier.lead_time_days} days."
            )
            for row in rows
        ]
        return ToolResult("get_low_stock_items", facts)

    def get_product(self, product_sku: str) -> ToolResult:
        safe_tool_log(logger, "get_product")
        sku = _validate_sku(product_sku)
        product = self.repository.get_product(sku)
        if not product:
            return ToolResult("get_product", [f"No product found for {sku}."])
        return ToolResult(
            "get_product",
            [
                (
                    f"{product.sku} is {product.name} in {product.category}; reorder point "
                    f"{product.reorder_point}, target stock {product.target_stock}, supplier "
                    f"{product.supplier.name}."
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
