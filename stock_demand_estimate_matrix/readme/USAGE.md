Make sure the estimating periods exist first — see the Configuration
section. If *Prepare* raises "There is no ranges created.", no range of
the selected *Date Range Type* overlaps the selected period; generate
them and try again.

To create or update estimates in bulk:

1. Go to *Inventory \> Demand Planning \> Create Stock Demand
   Estimates*.
2. Select the *Period* to estimate, the *Date Range Type*, the
   *Location* and the *Products* (at least one is required).
3. Click *Prepare*: a sheet opens as a matrix with one row per product
   and one column per range of the selected type overlapping the period,
   pre-filled with the existing estimates for that location.
4. Enter the expected quantity of each product in each period — in the
   product's unit of measure — and click *Validate*. One estimate per
   product and range is created, linked to the corresponding period;
   estimates that already exist are updated in place.

The resulting estimates are listed in *Inventory \> Demand Planning \>
Stock Demand Estimates* like manually created ones, with the estimating
period shown instead of manually entered dates. The list view is
editable, so single cells can still be corrected without reopening the
wizard.

**Example.** With a "Monthly" date range type and ranges generated for
January–March 2026, preparing a sheet for the period 01/01/2026 –
03/31/2026 with products *Office Chair* and *Desk* at location *WH/Stock*
opens a 2 × 3 matrix. Entering 100, 120 and 140 in the Office Chair row
and 50, 50 and 60 in the Desk row, then validating, creates six
estimates — e.g. "Jan 2026 - Office Chair - WH/Stock" for 100 units,
taking its dates and duration from the January range.
