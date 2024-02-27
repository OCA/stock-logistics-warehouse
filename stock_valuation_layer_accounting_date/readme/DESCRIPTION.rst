This module adds Accounting Date field in stock.valuation.layer, enabling the report
output based on this field.

Accounting Date is computed (and stored in the record) based on the following logic:

* If a journal entry is linked to the stock.valuation.layer record and its state is "post," use the date of the
  journal entry.
* If the first criterion is not met and a stock move is linked to the stock.valuation.layer, use the accounting date
  of the stock move.
* Otherwise, convert create_date (datetime) of the stock.valuation.layer record to date,
  with consideration to user's timezone.
