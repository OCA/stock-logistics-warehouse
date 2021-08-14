[![Build Status](https://travis-ci.org/OCA/stock-logistics-warehouse.svg?branch=8.0)](https://travis-ci.org/OCA/stock-logistics-warehouse)
[![Coverage Status](https://img.shields.io/coveralls/OCA/stock-logistics-warehouse/badge.png?branch=8.0)](https://coveralls.io/r/OCA/stock-logistics-warehouse?branch=8.0)

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
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_product](account_move_line_product/) | 8.0.1.0.0 |  | Account Move Line Product
[account_move_line_stock_info](account_move_line_stock_info/) | 8.0.1.0.0 |  | Account Move Line Stock Move
[business_product_location](business_product_location/) | 8.0.1.0.0 |  | Business Product Location
[partner_location_auto_create](partner_location_auto_create/) | 8.0.0.1.0 |  | Partner Location Auto Create
[stock_account_change_product_valuation](stock_account_change_product_valuation/) | 8.0.1.0.0 |  | Adjusts valuation of the products and quants when the cost method or type of a product changes
[stock_account_quant_merge](stock_account_quant_merge/) | 8.0.1.0.0 |  | Stock Account - Quant merge
[stock_available](stock_available/) | 8.0.3.1.0 |  | Stock available to promise
[stock_available_immediately](stock_available_immediately/) | 8.0.2.0.1 |  | Ignore planned receptions in quantity available to promise
[stock_available_lot_locked](stock_available_lot_locked/) | 8.0.1.0.0 |  | Consider the blocked lots are not available to promise
[stock_available_mrp](stock_available_mrp/) | 8.0.3.1.1 |  | Consider the production potential is available to promise
[stock_available_sale](stock_available_sale/) | 8.0.3.0.0 |  | Quotations in quantity available to promise
[stock_available_unreserved](stock_available_unreserved/) | 8.0.1.0.0 |  | Quantity of stock available for inmediate use
[stock_change_qty_reason](stock_change_qty_reason/) | 8.0.1.0.0 |  | Stock Quantity Change Reason
[stock_cycle_count](stock_cycle_count/) | 8.0.1.2.0 |  | Adds the capability to schedule cycle counts in a warehouse through different rules defined by the user
[stock_inventory_chatter](stock_inventory_chatter/) | 8.0.1.0.0 |  | Log changes being done in Inventory Adjustments
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 8.0.1.0.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_exclude_sublocation](stock_inventory_exclude_sublocation/) | 8.0.1.0.0 |  | Allow to perform inventories of a location without including its child locations.
[stock_inventory_exhaustive](stock_inventory_exhaustive/) | 8.0.1.0.0 |  | Remove from the stock what is not in the Physical Inventory.
[stock_inventory_hierarchical](stock_inventory_hierarchical/) | 8.0.2.0.0 |  | Group several Inventory adjustments in a master inventory
[stock_inventory_hierarchical_exhaustive](stock_inventory_hierarchical_exhaustive/) | 8.0.1.0.0 |  | Extra consistency checks
[stock_inventory_line_price](stock_inventory_line_price/) | 8.0.1.0.0 |  | Standard price at inventory level
[stock_inventory_lockdown](stock_inventory_lockdown/) | 8.0.1.0.0 |  | Lock down stock locations during inventories.
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 8.0.1.0.0 |  | More filters for inventory adjustments
[stock_inventory_revaluation](stock_inventory_revaluation/) | 8.0.1.1.0 |  | Introduces inventory revaluation as single point to change the valuation of products.
[stock_location_area_data](stock_location_area_data/) | 8.0.0.1.0 |  | Add surface units of measure
[stock_location_area_management](stock_location_area_management/) | 8.0.0.1.0 |  | Enter a location's area based on different units of measure
[stock_location_ownership](stock_location_ownership/) | 8.0.0.1.0 |  | Stock Location Ownership
[stock_lot_quantity](stock_lot_quantity/) | 8.0.1.0.0 |  | Stock quantity for serial number
[stock_mts_mto_rule](stock_mts_mto_rule/) | 8.0.1.0.1 |  | Add a MTS+MTO route
[stock_operation_type_location](stock_operation_type_location/) | 8.0.1.1.0 |  | Allows to filter locations on stock operations
[stock_orderpoint_generator](stock_orderpoint_generator/) | 8.0.1.0.0 |  | Mass configuration of stock order points
[stock_orderpoint_manual_procurement](stock_orderpoint_manual_procurement/) | 8.0.1.0.0 |  | Allows to create procurement orders from orderpoints instead of relying only on the scheduler
[stock_orderpoint_uom](stock_orderpoint_uom/) | 8.0.1.0.0 |  | Allows to create procurement orders in the UoM indicated in the orderpoint
[stock_product_location_sorted_by_qty](stock_product_location_sorted_by_qty/) | 8.0.1.0.0 |  | In the update wizard of quantities for a product, sort the stock location by quantity
[stock_putaway_product](stock_putaway_product/) | 8.0.1.0.1 |  | Set a product location and put-away strategy per product
[stock_quant_manual_assign](stock_quant_manual_assign/) | 8.0.1.2.1 |  | Stock - Manual assignment of quants
[stock_quant_merge](stock_quant_merge/) | 8.0.1.0.0 |  | Stock - Quant merge
[stock_quant_partner_info](stock_quant_partner_info/) | 8.0.1.1.0 |  | Stock - Quant partner info
[stock_reserve](stock_reserve/) | 8.0.0.2.0 |  | Stock reservations on products
[stock_reserve_sale](stock_reserve_sale/) | 8.0.1.0.1 |  | Stock Reserve Sales
[stock_traceability_operation](stock_traceability_operation/) | 8.0.1.1.0 |  | Adds operations in traceability and quant history
[stock_valuation_account_manual_adjustment](stock_valuation_account_manual_adjustment/) | 8.0.1.0.0 |  | Shows in the product inventory stock value and the accounting value and allows to reconcile them
[stock_warehouse_orderpoint_stock_info](stock_warehouse_orderpoint_stock_info/) | 8.0.1.0.0 |  | Reordering rules stock info


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[base_product_merge](base_product_merge/) | 1.0 (unported) |  | Base Products Merge
[configurable_stock_level](configurable_stock_level/) | 0.1 (unported) |  | name
[stock_lot_valuation](stock_lot_valuation/) | 0.1 (unported) |  | Lot Valuation
[stock_move_location](stock_move_location/) | 1.0 (unported) |  | Move Stock Location
[stock_optional_valuation](stock_optional_valuation/) | 0.1 (unported) |  | Stock optional valuation
[stock_orderpoint_creator](stock_orderpoint_creator/) | 1.0 (unported) |  | Configuration of order point in mass
[stock_reord_rule](stock_reord_rule/) | 0.2 (unported) |  | Improved reordering rules

[//]: # (end addons)
