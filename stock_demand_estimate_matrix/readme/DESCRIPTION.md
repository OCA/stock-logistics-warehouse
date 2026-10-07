Bulk entry of stock demand estimates through a spreadsheet-like wizard:
a matrix with one row per product and one column per estimating period,
where each cell holds the expected quantity.

The estimating periods are `date.range` records grouped under a *Date
Range Type* (provided by the `date_range` addon), such as "monthly" or
"weekly". Estimates created through the wizard are linked to their range
and take their dates and duration from it; they can be reviewed and
edited like any other demand estimate, and the list view becomes
editable for quick corrections.
