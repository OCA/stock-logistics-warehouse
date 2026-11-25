The estimating periods are `date.range` records and must be generated
before the wizard is used — `date_range` ships no default ranges.

1. Go to *Settings \> Technical \> Date ranges \> Date Range Types* and
   create a type, e.g. *Monthly*. This step can also be done from the
   generator below by creating the type on the fly.
2. Go to *Settings \> Technical \> Date ranges \> Generate Date Ranges*:
   select the type, the unit of time (e.g. months), a start date, and
   either an end date or a number of entries, then click *Generate*.
3. The generated ranges can be reviewed in *Inventory \> Configuration
   \> Date Ranges*.

Repeat the generation whenever estimates have to cover a period not yet
included in the existing ranges — otherwise the wizard raises "There is
no ranges created." when preparing the sheet.
