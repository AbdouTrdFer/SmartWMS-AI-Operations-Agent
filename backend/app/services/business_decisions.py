from dataclasses import dataclass
from enum import StrEnum

from app.models.wms import Inventory, Order, Product


class ReorderPriority(StrEnum):
    NONE = "none"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class InventoryPosition:
    sku: str
    warehouse_code: str
    on_hand_quantity: int
    reserved_quantity: int
    available_quantity: int
    reorder_point: int
    target_stock: int
    supplier_name: str
    supplier_lead_time_days: int
    supplier_reliability_score: float
    open_demand_quantity: int
    is_low_stock: bool
    is_stockout: bool
    stockout_gap_quantity: int
    suggested_reorder_quantity: int
    reorder_priority: ReorderPriority
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ProductDecisionProfile:
    sku: str
    name: str
    category: str
    reorder_point: int
    target_stock: int
    supplier_name: str
    supplier_lead_time_days: int
    supplier_reliability_score: float


class WMSBusinessDecisionService:
    """Deterministic WMS business rules consumed by tools and, later, AI agents."""

    LONG_LEAD_TIME_DAYS = 7
    LOWER_RELIABILITY_THRESHOLD = 0.9

    def build_product_profile(self, product: Product) -> ProductDecisionProfile:
        return ProductDecisionProfile(
            sku=product.sku,
            name=product.name,
            category=product.category,
            reorder_point=product.reorder_point,
            target_stock=product.target_stock,
            supplier_name=product.supplier.name,
            supplier_lead_time_days=product.supplier.lead_time_days,
            supplier_reliability_score=product.supplier.reliability_score,
        )

    def build_inventory_position(
        self,
        inventory: Inventory,
        open_orders: list[Order],
    ) -> InventoryPosition:
        available_quantity = self.available_quantity(
            inventory.quantity,
            inventory.reserved_quantity,
        )
        open_demand_quantity = self.open_demand_quantity(
            open_orders=open_orders,
            product_id=inventory.product_id,
            warehouse_id=inventory.warehouse_id,
        )
        is_low_stock = self.is_low_stock(available_quantity, inventory.product.reorder_point)
        stockout_gap_quantity = max(open_demand_quantity - available_quantity, 0)
        is_stockout = available_quantity <= 0 or stockout_gap_quantity > 0
        suggested_reorder_quantity = max(inventory.product.target_stock - available_quantity, 0)
        reason_codes = self.reason_codes(
            available_quantity=available_quantity,
            reorder_point=inventory.product.reorder_point,
            open_demand_quantity=open_demand_quantity,
            stockout_gap_quantity=stockout_gap_quantity,
            supplier_lead_time_days=inventory.product.supplier.lead_time_days,
            supplier_reliability_score=inventory.product.supplier.reliability_score,
        )
        priority = self.reorder_priority(
            is_low_stock=is_low_stock,
            is_stockout=is_stockout,
            supplier_lead_time_days=inventory.product.supplier.lead_time_days,
            supplier_reliability_score=inventory.product.supplier.reliability_score,
            open_demand_quantity=open_demand_quantity,
        )

        return InventoryPosition(
            sku=inventory.product.sku,
            warehouse_code=inventory.warehouse.code,
            on_hand_quantity=inventory.quantity,
            reserved_quantity=inventory.reserved_quantity,
            available_quantity=available_quantity,
            reorder_point=inventory.product.reorder_point,
            target_stock=inventory.product.target_stock,
            supplier_name=inventory.product.supplier.name,
            supplier_lead_time_days=inventory.product.supplier.lead_time_days,
            supplier_reliability_score=inventory.product.supplier.reliability_score,
            open_demand_quantity=open_demand_quantity,
            is_low_stock=is_low_stock,
            is_stockout=is_stockout,
            stockout_gap_quantity=stockout_gap_quantity,
            suggested_reorder_quantity=suggested_reorder_quantity,
            reorder_priority=priority,
            reason_codes=reason_codes,
        )

    def available_quantity(self, on_hand_quantity: int, reserved_quantity: int) -> int:
        return on_hand_quantity - reserved_quantity

    def is_low_stock(self, available_quantity: int, reorder_point: int) -> bool:
        return available_quantity < reorder_point

    def open_demand_quantity(
        self,
        open_orders: list[Order],
        product_id: int,
        warehouse_id: int,
    ) -> int:
        demand = 0
        for order in open_orders:
            if order.warehouse_id != warehouse_id:
                continue
            demand += sum(item.quantity for item in order.items if item.product_id == product_id)
        return demand

    def reorder_priority(
        self,
        is_low_stock: bool,
        is_stockout: bool,
        supplier_lead_time_days: int,
        supplier_reliability_score: float,
        open_demand_quantity: int,
    ) -> ReorderPriority:
        if is_stockout:
            return ReorderPriority.CRITICAL
        if not is_low_stock:
            return ReorderPriority.NONE
        if (
            open_demand_quantity > 0
            or supplier_lead_time_days >= self.LONG_LEAD_TIME_DAYS
            or supplier_reliability_score < self.LOWER_RELIABILITY_THRESHOLD
        ):
            return ReorderPriority.HIGH
        return ReorderPriority.MEDIUM

    def reason_codes(
        self,
        available_quantity: int,
        reorder_point: int,
        open_demand_quantity: int,
        stockout_gap_quantity: int,
        supplier_lead_time_days: int,
        supplier_reliability_score: float,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if available_quantity < reorder_point:
            reasons.append("AVAILABLE_BELOW_REORDER_POINT")
        if open_demand_quantity > 0:
            reasons.append("OPEN_DEMAND_EXISTS")
        if stockout_gap_quantity > 0:
            reasons.append("OPEN_DEMAND_EXCEEDS_AVAILABLE")
        if supplier_lead_time_days >= self.LONG_LEAD_TIME_DAYS:
            reasons.append("LONG_SUPPLIER_LEAD_TIME")
        if supplier_reliability_score < self.LOWER_RELIABILITY_THRESHOLD:
            reasons.append("LOWER_SUPPLIER_RELIABILITY")
        return tuple(reasons)
