from datetime import UTC, datetime, timedelta

from app.db.base import Base
from app.db.session import engine
from app.models.wms import (
    Inventory,
    Order,
    OrderItem,
    Product,
    StockMovement,
    Supplier,
    Warehouse,
)
from sqlalchemy import select
from sqlalchemy.orm import Session


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(Product).limit(1)):
        return

    suppliers = [
        Supplier(id=1, name="NorthStar Packaging", lead_time_days=4, reliability_score=0.96),
        Supplier(id=2, name="Vertex Safety Supply", lead_time_days=9, reliability_score=0.88),
        Supplier(id=3, name="Atlas Components", lead_time_days=12, reliability_score=0.82),
    ]
    warehouses = [
        Warehouse(id=1, code="WH-NJ", name="New Jersey DC", location="Newark, NJ"),
        Warehouse(id=2, code="WH-TX", name="Texas DC", location="Dallas, TX"),
    ]
    products = [
        Product(
            id=1,
            sku="SKU-101",
            name="12x10x8 Shipping Carton",
            category="Packaging",
            reorder_point=200,
            target_stock=800,
            supplier_id=1,
        ),
        Product(
            id=2,
            sku="SKU-102",
            name="Thermal Label Roll",
            category="Consumables",
            reorder_point=150,
            target_stock=650,
            supplier_id=1,
        ),
        Product(
            id=3,
            sku="SKU-205",
            name="Cut Resistant Gloves",
            category="Safety",
            reorder_point=75,
            target_stock=300,
            supplier_id=2,
        ),
        Product(
            id=4,
            sku="SKU-330",
            name="Scanner Battery Pack",
            category="Equipment",
            reorder_point=40,
            target_stock=120,
            supplier_id=3,
        ),
    ]
    now = datetime.now(UTC).replace(tzinfo=None)
    inventory = [
        Inventory(
            id=1,
            warehouse_id=1,
            product_id=1,
            quantity=520,
            reserved_quantity=120,
            updated_at=now,
        ),
        Inventory(
            id=2,
            warehouse_id=1,
            product_id=2,
            quantity=170,
            reserved_quantity=95,
            updated_at=now,
        ),
        Inventory(
            id=3,
            warehouse_id=1,
            product_id=3,
            quantity=64,
            reserved_quantity=12,
            updated_at=now,
        ),
        Inventory(
            id=4,
            warehouse_id=1,
            product_id=4,
            quantity=38,
            reserved_quantity=21,
            updated_at=now,
        ),
        Inventory(
            id=5,
            warehouse_id=2,
            product_id=2,
            quantity=240,
            reserved_quantity=40,
            updated_at=now,
        ),
        Inventory(
            id=6,
            warehouse_id=2,
            product_id=4,
            quantity=52,
            reserved_quantity=5,
            updated_at=now,
        ),
    ]
    orders = [
        Order(
            id=1,
            customer_reference="ORD-9001",
            warehouse_id=1,
            status="open",
            priority="high",
            created_at=now - timedelta(days=1),
        ),
        Order(
            id=2,
            customer_reference="ORD-9002",
            warehouse_id=1,
            status="open",
            priority="normal",
            created_at=now - timedelta(days=2),
        ),
        Order(
            id=3,
            customer_reference="ORD-9003",
            warehouse_id=2,
            status="open",
            priority="high",
            created_at=now - timedelta(hours=8),
        ),
    ]
    order_items = [
        OrderItem(id=1, order_id=1, product_id=2, quantity=80),
        OrderItem(id=2, order_id=1, product_id=4, quantity=18),
        OrderItem(id=3, order_id=2, product_id=3, quantity=10),
        OrderItem(id=4, order_id=3, product_id=2, quantity=35),
    ]
    movements = [
        StockMovement(
            id=1,
            warehouse_id=1,
            product_id=2,
            movement_type="pick",
            quantity=-80,
            timestamp=now - timedelta(hours=6),
        ),
        StockMovement(
            id=2,
            warehouse_id=1,
            product_id=2,
            movement_type="receipt",
            quantity=120,
            timestamp=now - timedelta(days=5),
        ),
        StockMovement(
            id=3,
            warehouse_id=1,
            product_id=4,
            movement_type="adjustment",
            quantity=-5,
            timestamp=now - timedelta(days=1),
        ),
        StockMovement(
            id=4,
            warehouse_id=2,
            product_id=2,
            movement_type="pick",
            quantity=-35,
            timestamp=now - timedelta(hours=3),
        ),
    ]

    db.add_all([*suppliers, *warehouses, *products, *inventory, *orders, *order_items, *movements])
    db.commit()
