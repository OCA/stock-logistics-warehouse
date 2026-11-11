This module adds the stock move to the account move lines that it
generates.

Since Odoo 19.0, a stock move only generates journal items when the
product uses automated valuation and its source or destination location
has a Stock Valuation Account set. That is mostly the case for virtual
locations such as inventory loss, scrap or production. Receipts from
vendors and deliveries to customers usually generate no journal items,
so there is nothing to link to them.
