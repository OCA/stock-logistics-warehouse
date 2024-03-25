This module add relationship on various stock models to warehouses (`stock.warehouse`).

This is technical modules to be use as base for other modules such as:

* **stock_multi_warehouse_security**: Add ir rules to restrict user access to a list of warehouses

Following models are linked by this module:

* *stock.picking*
* *stock.move*
* *stock.move.line*
* *stock.quant*
* *stock.quant.package*

This module is inspired from the experiences of
`stock_multi_warehouse_security <https://github.com/akretion/stock-logistics-warehouse/tree/12-muli-wh-security/stock_multi_warehouse_security/>`_
on version 12.0 but has some key differences on user experience:
