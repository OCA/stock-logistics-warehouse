[![Build Status](https://travis-ci.org/OCA/stock-logistics-warehouse.svg?branch=10.0)](https://travis-ci.org/OCA/stock-logistics-warehouse)
[![Coverage Status](https://img.shields.io/coveralls/OCA/stock-logistics-warehouse/badge.png?branch=10.0)](https://coveralls.io/r/OCA/stock-logistics-warehouse?branch=10.0)

Odoo Stock Logistic Warehouse
=============================


This project aim to deal with modules related to the management of warehouses. You'll find modules that:

 - Ease inventory by adding various possibilities
 - Move all product from one location to another
 - Manage the product catalog (merge them,..)

Please don't hesitate to suggest one of your module to this project. Also, you may want to have a look on those other projects here:

 - https://github.com/OCA/stock-logistics-tracking
 - https://github.com/OCA/stock-logistics-barcode
 - https://github.com/OCA/stock-logistics-workflow

[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[account_move_line_product](account_move_line_product/) | 10.0.1.0.0 | Displays the product in the journal entries and items
[account_move_line_stock_info](account_move_line_stock_info/) | 10.0.1.0.0 | Account Move Line Stock Move
[stock_available](stock_available/) | 10.0.1.0.0 | Stock available to promise
[stock_available_immediately](stock_available_immediately/) | 10.0.1.0.0 | Ignore planned receptions in quantity available to promise
[stock_available_unreserved](stock_available_unreserved/) | 10.0.1.0.0 | Quantity of stock available for immediate use
[stock_change_qty_reason](stock_change_qty_reason/) | 10.0.1.0.0 | Stock Quantity Change Reason
[stock_inventory_chatter](stock_inventory_chatter/) | 10.0.1.0.0 | Log changes being done in Inventory Adjustments
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 10.0.1.0.0 | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_exclude_sublocation](stock_inventory_exclude_sublocation/) | 10.0.1.0.0 | Allow to perform inventories of a location without including its child locations.
[stock_inventory_verification_request](stock_inventory_verification_request/) | 10.0.1.0.0 | Adds the capability to request a Slot Verification when a inventory is Pending to Approve
[stock_mts_mto_rule](stock_mts_mto_rule/) | 10.0.1.0.0 | Add a MTS+MTO route
[stock_operation_package_mandatory](stock_operation_package_mandatory/) | 10.0.1.0.0 | Makes destination package mandatory on stock pack operations
[stock_orderpoint_automatic_creation](stock_orderpoint_automatic_creation/) | 10.0.1.0.0 | Stock Orderpoint Automatic Creation
[stock_putaway_product](stock_putaway_product/) | 10.0.1.0.0 | Set a product location and put-away strategy per product
[stock_quant_manual_assign](stock_quant_manual_assign/) | 10.0.1.0.0 | Stock - Manual Quant Assignment
[stock_quant_merge](stock_quant_merge/) | 10.0.1.0.0 | Stock - Quant merge
[stock_quant_reserved_qty_uom](stock_quant_reserved_qty_uom/) | 10.0.1.0.0 | Stock Quant Reserved Qty UoM
[stock_reserve](stock_reserve/) | 10.0.1.0.0 | Stock reservations on products
[stock_warehouse_orderpoint_stock_info](stock_warehouse_orderpoint_stock_info/) | 10.0.1.0.0 | Stock Warehouse Orderpoint Stock Info


Unported addons
---------------
addon | version | summary
--- | --- | ---
[base_product_merge](base_product_merge/) | 1.0 (unported) | Base Products Merge
[configurable_stock_level](configurable_stock_level/) | 0.1 (unported) | name
[partner_location_auto_create](partner_location_auto_create/) | 0.1 (unported) | Partner Location Auto Create
[stock_available_mrp](stock_available_mrp/) | 9.0.1.0.0 (unported) | Consider the production potential is available to promise
[stock_available_sale](stock_available_sale/) | 2.0 (unported) | Quotations in quantity available to promise
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 8.0.1.0.0 (unported) | More filters for inventory adjustments
[stock_location_area_data](stock_location_area_data/) | 8.0.0.1.0 (unported) | Add surface units of measure
[stock_location_area_management](stock_location_area_management/) | 8.0.0.1.0 (unported) | Enter a location's area based on different units of measure
[stock_location_ownership](stock_location_ownership/) | 8.0.0.1.0 (unported) | Stock Location Ownership
[stock_lot_valuation](stock_lot_valuation/) | 0.1 (unported) | Lot Valuation
[stock_move_location](stock_move_location/) | 1.0 (unported) | Move Stock Location
[stock_optional_valuation](stock_optional_valuation/) | 0.1 (unported) | Stock optional valuation
[stock_orderpoint_creator](stock_orderpoint_creator/) | 1.0 (unported) | Configuration of order point in mass
[stock_partner_lot](stock_partner_lot/) | 9.0.1.0.0 (unported) | Show lots on the partners that own them
[stock_reord_rule](stock_reord_rule/) | 0.2 (unported) | Improved reordering rules
[stock_reserve_sale](stock_reserve_sale/) | 8.0.1.0.0 (unported) | Stock Reserve Sales

[//]: # (end addons)
