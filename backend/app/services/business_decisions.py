from dataclasses import asdict, dataclass
from enum import StrEnum

from app.models.wms import Inventory, Order, Product


class StockoutRisk(StrEnum):
    LOW = "LOW"
    HIGH = "HIGH"


class ReplenishmentPriorityBand(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ProductDecisionProfile:
    sku: str
    name: str
    category: str
    reorder_point: int
    target_stock: int | None
    supplier_name: str
    supplier_lead_time_days: int
    supplier_reliability_score: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class InventoryAnalysisResult:
    sku: str
    warehouse_code: str
    on_hand_quantity: int
    reserved_quantity: int
    inbound_quantity: int | None
    available_quantity: int
    inventory_position: int | None
    reorder_point: int
    target_stock: int | None
    supplier_lead_time_days: int
    supplier_reliability_score: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class DemandAnalysisResult:
    sku: str
    warehouse_code: str
    open_demand_quantity: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class StockoutRiskResult:
    sku: str
    warehouse_code: str
    available_quantity: int
    open_demand_quantity: int
    demand_shortfall_quantity: int
    stockout_risk: StockoutRisk
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ReorderQuantityResult:
    reorder_quantity: int | None
    insufficient_data: bool
    reason: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ReplenishmentAnalysisResult:
    sku: str
    warehouse_code: str
    on_hand_quantity: int
    reserved_quantity: int
    inbound_quantity: int | None
    available_quantity: int
    inventory_position: int | None
    reorder_point: int
    target_stock: int | None
    open_demand_quantity: int
    demand_shortfall_quantity: int
    low_stock_candidate: bool
    demand_shortfall: bool
    stockout_risk: StockoutRisk
    replenishment_candidate: bool
    reorder_quantity: int | None
    reorder_quantity_reason: str | None
    insufficient_data: bool
    stock_gap_score: float
    demand_pressure_score: float
    lead_time_score: float
    replenishment_priority_score: float
    replenishment_priority_band: ReplenishmentPriorityBand
    supplier_lead_time_days: int
    supplier_reliability_score: float
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class InboundQuantityProvider:
    """MVP inbound abstraction. Later implementations can read POs, ASNs, or transfers."""

    def get_inbound_quantity(self, sku: str, warehouse_code: str) -> int | None:
        raise NotImplementedError


class DemoInboundQuantityProvider(InboundQuantityProvider):
    def get_inbound_quantity(self, sku: str, warehouse_code: str) -> int | None:
        return 0


class WMSBusinessDecisionService:
    """Deterministic WMS rules consumed by tools and, later, AI agents."""

    LEAD_TIME_NORMALIZER_DAYS = 14
    STOCK_GAP_WEIGHT = 0.40
    DEMAND_PRESSURE_WEIGHT = 0.45
    LEAD_TIME_WEIGHT = 0.15
    STOCKOUT_RISK_SCORE_FLOOR = 0.75

    def __init__(self, inbound_provider: InboundQuantityProvider | None = None):
        self.inbound_provider = inbound_provider or DemoInboundQuantityProvider()

    def build_product_profile(self, product: Product) -> ProductDecisionProfile:
        self._validate_policy_quantity("reorder_point", product.reorder_point)
        self._validate_optional_policy_quantity("target_stock", product.target_stock)
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

    def build_inventory_analysis(self, inventory: Inventory) -> InventoryAnalysisResult:
        inbound_quantity = self._inbound_quantity(
            inventory.product.sku,
            inventory.warehouse.code,
        )
        available_quantity = self.available_quantity(
            inventory.quantity,
            inventory.reserved_quantity,
        )
        inventory_position = None
        if inbound_quantity is not None:
            inventory_position = self.inventory_position(
                on_hand_quantity=inventory.quantity,
                inbound_quantity=inbound_quantity,
                reserved_quantity=inventory.reserved_quantity,
            )
        self._validate_policy_quantity("reorder_point", inventory.product.reorder_point)
        self._validate_optional_policy_quantity("target_stock", inventory.product.target_stock)
        return InventoryAnalysisResult(
            sku=inventory.product.sku,
            warehouse_code=inventory.warehouse.code,
            on_hand_quantity=inventory.quantity,
            reserved_quantity=inventory.reserved_quantity,
            inbound_quantity=inbound_quantity,
            available_quantity=available_quantity,
            inventory_position=inventory_position,
            reorder_point=inventory.product.reorder_point,
            target_stock=inventory.product.target_stock,
            supplier_lead_time_days=inventory.product.supplier.lead_time_days,
            supplier_reliability_score=inventory.product.supplier.reliability_score,
        )

    def build_demand_analysis(
        self,
        inventory: Inventory,
        open_orders: list[Order],
    ) -> DemandAnalysisResult:
        return DemandAnalysisResult(
            sku=inventory.product.sku,
            warehouse_code=inventory.warehouse.code,
            open_demand_quantity=self.open_demand_quantity(
                open_orders=open_orders,
                product_id=inventory.product_id,
                warehouse_id=inventory.warehouse_id,
            ),
        )

    def build_stockout_risk(
        self,
        inventory_analysis: InventoryAnalysisResult,
        demand_analysis: DemandAnalysisResult,
    ) -> StockoutRiskResult:
        demand_shortfall_quantity = self.demand_shortfall_quantity(
            available_quantity=inventory_analysis.available_quantity,
            open_demand_quantity=demand_analysis.open_demand_quantity,
        )
        stockout_risk = self.stockout_risk(
            available_quantity=inventory_analysis.available_quantity,
            open_demand_quantity=demand_analysis.open_demand_quantity,
        )
        return StockoutRiskResult(
            sku=inventory_analysis.sku,
            warehouse_code=inventory_analysis.warehouse_code,
            available_quantity=inventory_analysis.available_quantity,
            open_demand_quantity=demand_analysis.open_demand_quantity,
            demand_shortfall_quantity=demand_shortfall_quantity,
            stockout_risk=stockout_risk,
            reason_codes=self.stockout_reason_codes(
                inventory_analysis.available_quantity,
                demand_shortfall_quantity,
            ),
        )

    def build_replenishment_analysis(
        self,
        inventory: Inventory,
        open_orders: list[Order],
    ) -> ReplenishmentAnalysisResult:
        inventory_analysis = self.build_inventory_analysis(inventory)
        demand_analysis = self.build_demand_analysis(inventory, open_orders)
        stockout = self.build_stockout_risk(inventory_analysis, demand_analysis)
        low_stock_candidate = self.low_stock_candidate(
            inventory_analysis.available_quantity,
            inventory_analysis.reorder_point,
        )
        demand_shortfall = stockout.demand_shortfall_quantity > 0
        replenishment_candidate = self.replenishment_candidate(
            low_stock_candidate,
            stockout.demand_shortfall_quantity,
        )
        reorder_quantity = self.reorder_quantity(
            target_stock=inventory_analysis.target_stock,
            inventory_position=inventory_analysis.inventory_position,
            inbound_quantity=inventory_analysis.inbound_quantity,
        )
        stock_gap_score = self.stock_gap_score(
            available_quantity=inventory_analysis.available_quantity,
            reorder_point=inventory_analysis.reorder_point,
        )
        demand_pressure_score = self.demand_pressure_score(
            available_quantity=inventory_analysis.available_quantity,
            open_demand_quantity=demand_analysis.open_demand_quantity,
        )
        lead_time_score = self.lead_time_score(inventory_analysis.supplier_lead_time_days)
        priority_score = self.replenishment_priority_score(
            stock_gap_score=stock_gap_score,
            demand_pressure_score=demand_pressure_score,
            lead_time_score=lead_time_score,
            stockout_risk=stockout.stockout_risk,
        )

        return ReplenishmentAnalysisResult(
            sku=inventory_analysis.sku,
            warehouse_code=inventory_analysis.warehouse_code,
            on_hand_quantity=inventory_analysis.on_hand_quantity,
            reserved_quantity=inventory_analysis.reserved_quantity,
            inbound_quantity=inventory_analysis.inbound_quantity,
            available_quantity=inventory_analysis.available_quantity,
            inventory_position=inventory_analysis.inventory_position,
            reorder_point=inventory_analysis.reorder_point,
            target_stock=inventory_analysis.target_stock,
            open_demand_quantity=demand_analysis.open_demand_quantity,
            demand_shortfall_quantity=stockout.demand_shortfall_quantity,
            low_stock_candidate=low_stock_candidate,
            demand_shortfall=demand_shortfall,
            stockout_risk=stockout.stockout_risk,
            replenishment_candidate=replenishment_candidate,
            reorder_quantity=reorder_quantity.reorder_quantity,
            reorder_quantity_reason=reorder_quantity.reason,
            insufficient_data=reorder_quantity.insufficient_data,
            stock_gap_score=stock_gap_score,
            demand_pressure_score=demand_pressure_score,
            lead_time_score=lead_time_score,
            replenishment_priority_score=priority_score,
            replenishment_priority_band=self.replenishment_priority_band(priority_score),
            supplier_lead_time_days=inventory_analysis.supplier_lead_time_days,
            supplier_reliability_score=inventory_analysis.supplier_reliability_score,
            reason_codes=self.replenishment_reason_codes(
                low_stock_candidate=low_stock_candidate,
                demand_shortfall=demand_shortfall,
                stockout_risk=stockout.stockout_risk,
            ),
        )

    def available_quantity(self, on_hand_quantity: int, reserved_quantity: int) -> int:
        self._validate_operational_quantity("on_hand_quantity", on_hand_quantity)
        self._validate_operational_quantity("reserved_quantity", reserved_quantity)
        if reserved_quantity > on_hand_quantity:
            raise ValueError(
                "reserved_quantity cannot exceed on_hand_quantity; "
                "negative availability is not enabled for this MVP"
            )
        return on_hand_quantity - reserved_quantity

    def inventory_position(
        self,
        on_hand_quantity: int,
        inbound_quantity: int,
        reserved_quantity: int,
    ) -> int:
        self._validate_operational_quantity("on_hand_quantity", on_hand_quantity)
        self._validate_operational_quantity("inbound_quantity", inbound_quantity)
        self._validate_operational_quantity("reserved_quantity", reserved_quantity)
        return on_hand_quantity + inbound_quantity - reserved_quantity

    def open_demand_quantity(
        self,
        open_orders: list[Order],
        product_id: int,
        warehouse_id: int,
    ) -> int:
        demand = 0
        for order in open_orders:
            if order.status != "open" or order.warehouse_id != warehouse_id:
                continue
            for item in order.items:
                if item.product_id != product_id:
                    continue
                self._validate_operational_quantity("order_item_quantity", item.quantity)
                demand += item.quantity
        return demand

    def low_stock_candidate(self, available_quantity: int, reorder_point: int) -> bool:
        self._validate_policy_quantity("reorder_point", reorder_point)
        return available_quantity < reorder_point

    def demand_shortfall_quantity(
        self,
        available_quantity: int,
        open_demand_quantity: int,
    ) -> int:
        self._validate_operational_quantity("open_demand_quantity", open_demand_quantity)
        return max(open_demand_quantity - available_quantity, 0)

    def stockout_risk(
        self,
        available_quantity: int,
        open_demand_quantity: int,
    ) -> StockoutRisk:
        if available_quantity <= 0:
            return StockoutRisk.HIGH
        if available_quantity < open_demand_quantity:
            return StockoutRisk.HIGH
        return StockoutRisk.LOW

    def replenishment_candidate(
        self,
        low_stock_candidate: bool,
        demand_shortfall_quantity: int,
    ) -> bool:
        return low_stock_candidate or demand_shortfall_quantity > 0

    def reorder_quantity(
        self,
        target_stock: int | None,
        inventory_position: int | None,
        inbound_quantity: int | None,
    ) -> ReorderQuantityResult:
        if target_stock is None or inventory_position is None or inbound_quantity is None:
            return ReorderQuantityResult(
                reorder_quantity=None,
                insufficient_data=True,
                reason="INSUFFICIENT_DATA",
            )
        self._validate_policy_quantity("target_stock", target_stock)
        self._validate_operational_quantity("inbound_quantity", inbound_quantity)
        return ReorderQuantityResult(
            reorder_quantity=max(target_stock - inventory_position, 0),
            insufficient_data=False,
            reason=None,
        )

    def stock_gap_score(self, available_quantity: int, reorder_point: int) -> float:
        if reorder_point <= 0:
            return 0.0
        return self._clamp((reorder_point - available_quantity) / reorder_point)

    def demand_pressure_score(
        self,
        available_quantity: int,
        open_demand_quantity: int,
    ) -> float:
        if open_demand_quantity <= 0:
            return 0.0
        if available_quantity <= 0:
            return 1.0
        return self._clamp(open_demand_quantity / available_quantity)

    def lead_time_score(self, supplier_lead_time_days: int) -> float:
        self._validate_operational_quantity("supplier_lead_time_days", supplier_lead_time_days)
        return self._clamp(supplier_lead_time_days / self.LEAD_TIME_NORMALIZER_DAYS)

    def replenishment_priority_score(
        self,
        stock_gap_score: float,
        demand_pressure_score: float,
        lead_time_score: float,
        stockout_risk: StockoutRisk,
    ) -> float:
        weighted_score = (
            self.STOCK_GAP_WEIGHT * stock_gap_score
            + self.DEMAND_PRESSURE_WEIGHT * demand_pressure_score
            + self.LEAD_TIME_WEIGHT * lead_time_score
        )
        if stockout_risk == StockoutRisk.HIGH:
            weighted_score = max(weighted_score, self.STOCKOUT_RISK_SCORE_FLOOR)
        return round(self._clamp(weighted_score), 3)

    def replenishment_priority_band(
        self,
        replenishment_priority_score: float,
    ) -> ReplenishmentPriorityBand:
        if replenishment_priority_score <= 0:
            return ReplenishmentPriorityBand.NONE
        if replenishment_priority_score >= 0.70:
            return ReplenishmentPriorityBand.HIGH
        if replenishment_priority_score >= 0.35:
            return ReplenishmentPriorityBand.MEDIUM
        return ReplenishmentPriorityBand.LOW

    def stockout_reason_codes(
        self,
        available_quantity: int,
        demand_shortfall_quantity: int,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if available_quantity <= 0:
            reasons.append("NO_AVAILABLE_STOCK")
        if demand_shortfall_quantity > 0:
            reasons.append("OPEN_DEMAND_EXCEEDS_AVAILABLE")
        return tuple(reasons)

    def replenishment_reason_codes(
        self,
        low_stock_candidate: bool,
        demand_shortfall: bool,
        stockout_risk: StockoutRisk,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if low_stock_candidate:
            reasons.append("AVAILABLE_BELOW_REORDER_POINT")
        if demand_shortfall:
            reasons.append("OPEN_DEMAND_EXCEEDS_AVAILABLE")
        if stockout_risk == StockoutRisk.HIGH:
            reasons.append("HIGH_STOCKOUT_RISK")
        return tuple(reasons)

    def _inbound_quantity(self, sku: str, warehouse_code: str) -> int | None:
        inbound_quantity = self.inbound_provider.get_inbound_quantity(sku, warehouse_code)
        if inbound_quantity is None:
            return None
        self._validate_operational_quantity("inbound_quantity", inbound_quantity)
        return inbound_quantity

    def _validate_operational_quantity(self, field_name: str, value: int) -> None:
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative")

    def _validate_policy_quantity(self, field_name: str, value: int) -> None:
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative")

    def _validate_optional_policy_quantity(self, field_name: str, value: int | None) -> None:
        if value is not None:
            self._validate_policy_quantity(field_name, value)

    def _clamp(self, value: float) -> float:
        return max(0.0, min(value, 1.0))
