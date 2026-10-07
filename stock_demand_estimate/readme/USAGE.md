Estimates can be recorded one by one or, when the
`stock_demand_estimate_matrix` addon is installed, entered in bulk
through a products × periods wizard (see that module's documentation).

To create or review demand estimates, go to *Inventory \> Demand Planning
\> Stock Demand Estimates*. By default only the estimates that have not
expired are shown; use the *Expired* or *All (Active/Inactive)* filters to
change this.

To create an estimate:

1. Click *New* and select the product and the stock location the estimate
   applies to.
2. Define the period, either by entering a *Date From* and a *Date To*, or
   a *Date From* and a *Duration* in days; the missing value is filled in
   automatically. If no start date is set, the current date is assumed.
3. Enter the expected *Quantity* and, optionally, a *Unit of measure*
   different from the product's default one. The quantity is always stored
   in the product's unit of measure.
4. The *Quantity / Day* field shows the estimate evenly distributed over
   the period.

Estimates can be analyzed from the same menu using the pivot and graph
views, and grouped by product, location, period start or company. Once a
period is over, estimates can be archived instead of deleted, so that
historical expectations are kept.

Inventory users can read estimates; only inventory managers can create,
modify or delete them.

**Example.** You expect to sell about 120 units of the product "Office
Chair" from location WH/Stock during October 2026:

1. Create an estimate with product *Office Chair* and location
   *WH/Stock*.
2. Set *Date From* to 10/01/2026 and *Duration* to 31 days — *Date To*
   is filled in as 10/31/2026. Entering the *Date To* directly works the
   same way: the *Duration* is then computed from the two dates.
3. Set *Quantity* to 120 Units. If your forecast was made in dozens you
   can instead enter 10 with *Dozen* as the unit of measure — the stored
   quantity is the same either way.

The estimate then shows a *Quantity / Day* of about 3.87. Other modules
can ask how much of that demand falls inside any sub-period: for the
range 10/10/2026 – 10/20/2026 they get 11 days × 3.87 ≈ 42.6 units.

For developers: `estimate.get_quantity_by_date_range(date_start,
date_end)` returns the proportional part of the estimate that overlaps
the given range (≈ 42.6 units in the example above), or 0 when the
periods do not overlap.
