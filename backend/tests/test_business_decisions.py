from app.db.base import Base
from app.db.seed import seed_demo_data
from app.repositories.wms_repository import WMSRepository
from app.services.business_decisions import ReorderPriority, WMSBusinessDecisionService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def build_repository() -> WMSRepository:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    seed_demo_data(db)
    return WMSRepository(db)


def test_inventory_position_formalizes_stockout_and_reorder_priority() -> None:
    repository = build_repository()
    service = WMSBusinessDecisionService()
    inventory = repository.get_inventory("SKU-102", "WH-NJ")[0]
    open_orders = repository.get_open_orders("WH-NJ")

    position = service.build_inventory_position(inventory, open_orders)

    assert position.available_quantity == 75
    assert position.open_demand_quantity == 80
    assert position.is_low_stock is True
    assert position.is_stockout is True
    assert position.stockout_gap_quantity == 5
    assert position.reorder_priority == ReorderPriority.CRITICAL
    assert position.suggested_reorder_quantity == 575
    assert "AVAILABLE_BELOW_REORDER_POINT" in position.reason_codes
    assert "OPEN_DEMAND_EXCEEDS_AVAILABLE" in position.reason_codes


def test_inventory_position_marks_long_lead_time_low_stock_as_high_priority() -> None:
    repository = build_repository()
    service = WMSBusinessDecisionService()
    inventory = repository.get_inventory("SKU-205", "WH-NJ")[0]
    open_orders = repository.get_open_orders("WH-NJ")

    position = service.build_inventory_position(inventory, open_orders)

    assert position.available_quantity == 52
    assert position.open_demand_quantity == 10
    assert position.is_stockout is False
    assert position.reorder_priority == ReorderPriority.HIGH
    assert "LONG_SUPPLIER_LEAD_TIME" in position.reason_codes
    assert "LOWER_SUPPLIER_RELIABILITY" in position.reason_codes
