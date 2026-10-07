Manually record demand estimates: the quantity of a product that is
expected to be consumed or shipped from a given stock location over a
period of time.

Each estimate defines:

- A product and a stock location.
- A time period, expressed either as an explicit date range or as a start
  date plus a duration in days.
- An expected quantity, which can be entered in any unit of measure
  compatible with the product.

Estimates are stored together with their equivalent daily quantity, so the
expected demand can be evenly distributed or aggregated over any
sub-period. They are also multi-company aware: each estimate belongs to a
single company and its product and location must be consistent with it.

No specific usage of the estimates is provided out of the box — the data
model, a user interface to maintain them, and a small API
(`get_quantity_by_date_range`) are included so that other modules can
consume them. For example, `mrp_multi_level_estimate` (OCA/manufacture)
feeds these estimates into the MRP multi-level calculation.
