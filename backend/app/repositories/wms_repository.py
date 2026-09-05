from datetime import UTC, datetime, timedelta

from app.models.wms import Inventory, Order, OrderItem, Product, StockMovement, Supplier, Warehouse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload


class WMSRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_product(self, sku: str) -> Product | None:
        return self.db.scalar(
            select(Product).options(joinedload(Product.supplier)).where(Product.sku == sku)
        )

    def get_supplier(self, supplier_id: int) -> Supplier | None:
        return self.db.get(Supplier, supplier_id)

    def get_inventory(self, sku: str, warehouse_code: str | None = None) -> list[Inventory]:
        statement = (
            select(Inventory)
            .join(Inventory.product)
            .join(Inventory.warehouse)
            .options(
                joinedload(Inventory.product).joinedload(Product.supplier),
                joinedload(Inventory.warehouse),
            )
            .where(Product.sku == sku)
        )
        if warehouse_code:
            statement = statement.where(Warehouse.code == warehouse_code)
        return list(self.db.scalars(statement))

    def get_inventory_positions(self, warehouse_code: str | None = None) -> list[Inventory]:
        statement = (
            select(Inventory)
            .join(Inventory.product)
            .join(Inventory.warehouse)
            .options(
                joinedload(Inventory.product).joinedload(Product.supplier),
                joinedload(Inventory.warehouse),
            )
        )
        if warehouse_code:
            statement = statement.where(Warehouse.code == warehouse_code)
        return list(self.db.scalars(statement))

    def get_open_orders(self, warehouse_code: str | None = None) -> list[Order]:
        statement = (
            select(Order)
            .join(Order.warehouse)
            .options(
                joinedload(Order.warehouse),
                joinedload(Order.items).joinedload(OrderItem.product),
            )
            .where(Order.status == "open")
        )
        if warehouse_code:
            statement = statement.where(Warehouse.code == warehouse_code)
        return list(self.db.scalars(statement).unique())

    def get_stock_movements(self, sku: str, days: int) -> list[StockMovement]:
        since = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)
        statement = (
            select(StockMovement)
            .join(StockMovement.product)
            .join(StockMovement.warehouse)
            .options(joinedload(StockMovement.product), joinedload(StockMovement.warehouse))
            .where(Product.sku == sku, StockMovement.timestamp >= since)
            .order_by(StockMovement.timestamp.desc())
        )
        return list(self.db.scalars(statement))
