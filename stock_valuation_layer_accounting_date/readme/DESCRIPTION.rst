This module adds Accounting Date field in stock.valuation.layer, enabling the report
output based on this field.

Accounting Date is computed (and stored in the record) based on the following logic:

* If a journal entry linked to the stock.valuation.layer record, take the date of the
  journal entry.
* Otherwise, convert create_date (datetime) of the stock.valuation.layer record to date,
  with consideration to user's timezone.
