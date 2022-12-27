Use the Actual Date field in the following transfer and scrap scenarios:

- If you are late in processing a transfer or scrap in Odoo and wish to
  record the transaction with the actual transfer date, fill in the
  Actual Date field in the picking or scrap form. The Actual Date of the
  picking or scrap is then propagated to its corresponding stock moves
  and stock move lines, and is also passed to the journal entry as the
  date.
- You can also update the Actual Date of a completed picking or scrap if
  you belong to the 'Modify Actual Date' group. This operation updates
  the date of the related journal entries, re-proposing a new sequence
  to them as necessary.

Use the Actual Date field in the following stock valuation reporting scenarios:

1.  Go to *Inventory \> Reporting \> Inventory Valuation* and click
    'Inventory at Date'.
2.  In the wizard, select a date in 'Inventory at Date', and click
    'Valuation as of Accounting Date' (note that 'hh:mm:ss' part of the
    selection in 'Inventory at Date' is ignored in this context).
