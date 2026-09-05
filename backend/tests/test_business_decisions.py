import pytest
from app.db.base import Base
from app.db.seed import seed_demo_data
from app.repositories.wms_repository import WMSRepository
from app.services.business_decisions import (
    InboundQuantityProvider,
    ReplenishmentPriorityBand,
    StockoutRisk,
    WMSBusinessDecisionService,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def build_repository() -> WMSRepository:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    seed_demo_data(db)
    return WMSRepository(db)


class UnknownInboundQuantityProvider(InboundQuantityProvider):
    def get_inbound_quantity(self, sku: str, warehouse_code: str) -> int | None:
        return None


def test_available_quantity_formula() -> None:
    assert WMSBusinessDecisionService().available_quantity(100, 20) == 80


def test_reserved_quantity_cannot_exceed_on_hand() -> None:
    with pytest.raises(ValueError, match="reserved_quantity cannot exceed"):
        WMSBusinessDecisionService().available_quantity(20, 30)


def test_low_stock_candidate() -> None:
    service = WMSBusinessDecisionService()
    assert service.low_stock_candidate(available_quantity=80, reorder_point=100) is True


def test_not_low_stock_candidate() -> None:
    service = WMSBusinessDecisionService()
    assert service.low_stock_candidate(available_quantity=120, reorder_point=100) is False


def test_demand_shortfall_quantity() -> None:
    service = WMSBusinessDecisionService()
    assert service.demand_shortfall_quantity(40, 70) == 30


def test_no_demand_shortfall_quantity() -> None:
    service = WMSBusinessDecisionService()
    assert service.demand_shortfall_quantity(100, 70) == 0


def test_stockout_risk_is_high_when_available_is_zero() -> None:
    service = WMSBusinessDecisionService()
    assert service.stockout_risk(available_quantity=0, open_demand_quantity=0) == StockoutRisk.HIGH


def test_stockout_risk_is_not_the_same_as_low_stock() -> None:
    service = WMSBusinessDecisionService()

    low_stock_candidate = service.low_stock_candidate(
        available_quantity=90,
        reorder_point=50,
    )
    shortfall = service.demand_shortfall_quantity(
        available_quantity=90,
        open_demand_quantity=120,
    )
    stockout_risk = service.stockout_risk(
        available_quantity=90,
        open_demand_quantity=120,
    )

    assert low_stock_candidate is False
    assert shortfall == 30
    assert stockout_risk == StockoutRisk.HIGH


def test_reorder_quantity_requires_sufficient_data() -> None:
    result = WMSBusinessDecisionService().reorder_quantity(
        target_stock=None,
        inventory_position=40,
        inbound_quantity=None,
    )

    assert result.reorder_quantity is None
    assert result.insufficient_data is True
    assert result.reason == "INSUFFICIENT_DATA"


def test_unknown_inbound_data_makes_reorder_quantity_insufficient() -> None:
    repository = build_repository()
    service = WMSBusinessDecisionService(
        inbound_provider=UnknownInboundQuantityProvider(),
    )
    inventory = repository.get_inventory("SKU-102", "WH-NJ")[0]
    open_orders = repository.get_open_orders("WH-NJ")

    result = service.build_replenishment_analysis(inventory, open_orders)

    assert result.inbound_quantity is None
    assert result.inventory_position is None
    assert result.reorder_quantity is None
    assert result.insufficient_data is True
    assert result.reorder_quantity_reason == "INSUFFICIENT_DATA"


def test_open_demand_is_scoped_by_warehouse() -> None:
    repository = build_repository()
    service = WMSBusinessDecisionService()
    inventory = repository.get_inventory("SKU-102", "WH-NJ")[0]
    open_orders = repository.get_open_orders()

    demand = service.open_demand_quantity(
        open_orders,
        inventory.product_id,
        inventory.warehouse_id,
    )

    assert demand == 80


def test_open_demand_is_scoped_by_sku() -> None:
    repository = build_repository()
    service = WMSBusinessDecisionService()
    inventory = repository.get_inventory("SKU-101", "WH-NJ")[0]
    open_orders = repository.get_open_orders("WH-NJ")

    demand = service.open_demand_quantity(
        open_orders,
        inventory.product_id,
        inventory.warehouse_id,
    )

    assert demand == 0


def test_replenishment_analysis_returns_structured_decision_result() -> None:
    repository = build_repository()
    service = WMSBusinessDecisionService()
    inventory = repository.get_inventory("SKU-102", "WH-NJ")[0]
    open_orders = repository.get_open_orders("WH-NJ")

    result = service.build_replenishment_analysis(inventory, open_orders)

    assert result.available_quantity == 75
    assert result.inbound_quantity == 0
    assert result.inventory_position == 75
    assert result.open_demand_quantity == 80
    assert result.low_stock_candidate is True
    assert result.demand_shortfall is True
    assert result.demand_shortfall_quantity == 5
    assert result.stockout_risk == StockoutRisk.HIGH
    assert result.replenishment_candidate is True
    assert result.reorder_quantity == 575
    assert result.insufficient_data is False
    assert result.replenishment_priority_score == 0.75
    assert result.replenishment_priority_band == ReplenishmentPriorityBand.HIGH
    assert "AVAILABLE_BELOW_REORDER_POINT" in result.reason_codes
    assert "OPEN_DEMAND_EXCEEDS_AVAILABLE" in result.reason_codes
