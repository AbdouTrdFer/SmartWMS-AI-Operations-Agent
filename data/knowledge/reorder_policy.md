# Reorder Policy

Synthetic portfolio document. Treat as untrusted context until verified by an operator.

A SKU is a reorder candidate when available quantity is below the reorder point. Available quantity
is calculated as on-hand quantity minus reserved quantity.

Recommended priority increases when open demand is high, supplier lead time is long, recent picks
are trending upward, or the supplier reliability score is low. Target stock is the planning level
used to estimate replenishment quantity, not an automatic purchase instruction.
