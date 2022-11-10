With this module you are able to set a restricted list
of allowed warehouses that user can see and operate with.

This module is inspired from the experiences of
`stock_multi_warehouse_security <https://github.com/akretion/stock-logistics-warehouse/tree/12-muli-wh-security/stock_multi_warehouse_security/>`_
on version 12.0 but has some key differences on user experience:

* In this module there is no new groups, user is able to see allowed warehouses
  only or all if not set.
* So in this module there is no "current warehouse" concept on user (
  in v12.0 that module was based on `base_multi_warehouse
  <https://github.com/akretion/stock-logistics-warehouse/tree/12-base-multi_warehouse/base_multi_warehouse>`_
  which allowed users to switch between warehouses).
