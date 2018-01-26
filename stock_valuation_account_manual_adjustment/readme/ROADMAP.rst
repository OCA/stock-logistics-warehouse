* In order to properly manage the inventory valuation from an accounting
  perspective all journal items created for inventory accounts should
  include the product.
* The price change function of Odoo creates journal entries to the inventory
  account without specifying the product. This is bad because you lose the
  ability to control the inventory valuation from accounting at the level of
  the product. In order to fix this, use the module
  'stock_inventory_revaluation', to be found in the same OCA repository.

Points to be considered by contributors for future improvements are:

* This module does not support multi-company environments currently.
* Obtaining the valuation by product is currently mainly done by raw SQL
  queries. This could be improved to take advantage of ORM methods (like
  `read_group`)