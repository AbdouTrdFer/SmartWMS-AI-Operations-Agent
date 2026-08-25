from app.db.base import Base
from app.db.seed import seed_demo_data
from app.repositories.wms_repository import WMSRepository
from app.tools.wms_tools import WMSTools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def build_tools() -> WMSTools:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    seed_demo_data(db)
    return WMSTools(WMSRepository(db))


def test_low_stock_uses_available_quantity() -> None:
    result = build_tools().get_low_stock_items("WH-NJ")
    joined = "\n".join(result.facts)
    assert "SKU-102" in joined
    assert "available 75 vs reorder point 150" in joined


def test_invalid_sku_is_rejected() -> None:
    tools = build_tools()
    try:
        tools.get_inventory("SKU-102; drop table products")
    except ValueError as exc:
        assert "Invalid product_sku" in str(exc)
    else:
        raise AssertionError("invalid sku should be rejected")
