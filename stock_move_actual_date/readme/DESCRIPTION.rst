This module adds an Actual Date field to the stock picking, stock scrap,
stock move, and stock move line models. This field allows users to
record the actual date on which a stock transfer or stock scrap took
place, in case the transaction in Odoo is processed after the fact.

It also adds an Actual Date field to the Stock Valuation Layer model,
enabling reporting based on this field. This field is computed
and stored according to the following logic:

- If a posted journal entry exists, its date is used.
- If there is no journal entry, the stock move's actual date is used
- Otherwise, convert create_date (datetime) of the stock.valuation.layer
  record to date, with consideration to user's timezone.
