# WMS Domain Context

A Warehouse Management System manages receiving, inventory, picking, packing, shipping, stock
movements, and replenishment.

Key concepts:
- On-hand quantity: physical quantity recorded in inventory.
- Reserved quantity: quantity allocated to orders.
- Available quantity: on-hand minus reserved.
- Reorder point: threshold at which replenishment should be considered.
- Target stock: desired level after replenishment.
- Lead time: expected supplier delivery time.
- Stockout: no available quantity for demand.
- Stock movement: receipt, pick, adjustment, transfer, or shipment.

Illustrative rule:

```text
available_quantity = quantity - reserved_quantity
if available_quantity < reorder_point:
    low_stock_candidate = true
```
