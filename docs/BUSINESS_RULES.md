# SmartWMS Business Rules

This document defines the deterministic Day 1 WMS decision rules. These rules are implemented in
`backend/app/services/business_decisions.py` and are safe for later agent consumption.

## Inventory Position

Available quantity:

```text
available_quantity = on_hand_quantity - reserved_quantity
```

Low stock:

```text
is_low_stock = available_quantity < reorder_point
```

Open demand:

```text
open_demand_quantity = sum(open order item quantities for the same SKU and warehouse)
```

Stockout:

```text
stockout_gap_quantity = max(open_demand_quantity - available_quantity, 0)
is_stockout = available_quantity <= 0 OR stockout_gap_quantity > 0
```

Suggested reorder quantity:

```text
suggested_reorder_quantity = max(target_stock - available_quantity, 0)
```

## Reorder Priority

Priority is deterministic:

- `critical`: stockout exists.
- `none`: item is not low stock.
- `high`: item is low stock and has open demand, long supplier lead time, or lower supplier
  reliability.
- `medium`: item is low stock without the high-risk signals above.

Day 1 thresholds:

- Long supplier lead time: `>= 7` days.
- Lower supplier reliability: `< 0.90`.

## Reason Codes

The service emits reason codes so an AI layer can explain recommendations without inventing logic:

- `AVAILABLE_BELOW_REORDER_POINT`
- `OPEN_DEMAND_EXISTS`
- `OPEN_DEMAND_EXCEEDS_AVAILABLE`
- `LONG_SUPPLIER_LEAD_TIME`
- `LOWER_SUPPLIER_RELIABILITY`

These codes are operational signals, not autonomous purchase approvals.
