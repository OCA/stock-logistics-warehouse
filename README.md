[![Build Status](https://travis-ci.org/OCA/stock-logistics-warehouse.svg?branch=10.0)](https://travis-ci.org/OCA/stock-logistics-warehouse)
[![Coverage Status](https://img.shields.io/coveralls/OCA/stock-logistics-warehouse/badge.png?branch=10.0)](https://coveralls.io/r/OCA/stock-logistics-warehouse?branch=10.0)

Odoo Stock Logistics Warehouse
==============================


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
[packaging_uom](packaging_uom/) | 10.0.1.0.1 | Use uom in package
[packaging_uom_view](packaging_uom_view/) | 10.0.1.0.0 | If purchase is installed along with packaging_uom, there is a duplicate view
[procurement_auto_create_group](procurement_auto_create_group/) | 10.0.1.0.0 | Allows to configure the system to propose automatically new procurement groups in procurement orders.
[purchase_packaging](purchase_packaging/) | 10.0.1.0.8 | In purchase, use package
[sale_packaging](sale_packaging/) | 10.0.1.0.1 | In sale, use uom's package
[stock_account_change_product_valuation](stock_account_change_product_valuation/) | 10.0.1.0.0 | Adjusts valuation of the products and quants when the cost method or type of a product changes
[stock_account_quant_merge](stock_account_quant_merge/) | 10.0.1.0.0 | extension of 'stock_quant_merge', and adds the cost as a criteria to merge quants.
[stock_available](stock_available/) | 10.0.1.0.1 | Stock available to promise
[stock_available_immediately](stock_available_immediately/) | 10.0.1.0.0 | Ignore planned receptions in quantity available to promise
[stock_available_mrp](stock_available_mrp/) | 10.0.1.0.2 | Consider the production potential is available to promise
[stock_available_product_expiry](stock_available_product_expiry/) | 10.0.1.0.3 | Allows to get product availability taking into account lot removal date
[stock_available_sale](stock_available_sale/) | 10.0.1.0.0 | Quotations in quantity available to promise
[stock_available_unreserved](stock_available_unreserved/) | 10.0.1.0.1 | Quantity of stock available for immediate use
[stock_change_qty_reason](stock_change_qty_reason/) | 10.0.1.0.0 | Stock Quantity Change Reason
[stock_cycle_count](stock_cycle_count/) | 10.0.1.0.0 | Adds the capability to schedule cycle counts in a warehouse through different rules defined by the user.
[stock_demand_estimate](stock_demand_estimate/) | 10.0.1.1.0 | Allows to create demand estimates.
[stock_inventory_chatter](stock_inventory_chatter/) | 10.0.1.0.0 | Log changes being done in Inventory Adjustments
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 10.0.1.0.0 | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_exclude_sublocation](stock_inventory_exclude_sublocation/) | 10.0.1.0.0 | Allow to perform inventories of a location without including its child locations.
[stock_inventory_lockdown](stock_inventory_lockdown/) | 10.0.1.0.2 | Lock down stock locations during inventories.
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 10.0.1.0.0 | More filters for inventory adjustments
[stock_inventory_revaluation](stock_inventory_revaluation/) | 10.0.1.1.0 | Introduces inventory revaluation as single point to change the valuation of products.
[stock_inventory_verification_request](stock_inventory_verification_request/) | 10.0.1.0.0 | Adds the capability to request a Slot Verification when a inventory is Pending to Approve
[stock_location_lockdown](stock_location_lockdown/) | 10.0.1.1.0 | Prevent to add stock on flagged locations
[stock_location_restrict_procurement_group](stock_location_restrict_procurement_group/) | 10.0.1.1.0 | Allows to restrict location to a dedicated procurement group (e.g. : For orders waiting delivery)
[stock_lot_sale_tracking](stock_lot_sale_tracking/) | 10.0.1.0.0 | This addon allows to retrieve all customer deliveries impacted by a lot
[stock_mts_mto_rule](stock_mts_mto_rule/) | 10.0.1.0.3 | Add a MTS+MTO route
[stock_operation_package_mandatory](stock_operation_package_mandatory/) | 10.0.1.0.0 | Makes destination package mandatory on stock pack operations
[stock_orderpoint_automatic_creation](stock_orderpoint_automatic_creation/) | 10.0.1.0.0 | Stock Orderpoint Automatic Creation
[stock_orderpoint_manual_procurement](stock_orderpoint_manual_procurement/) | 10.0.1.0.0 | Allows to create procurement orders from orderpoints instead of relying only on the scheduler.
[stock_orderpoint_manual_procurement_uom](stock_orderpoint_manual_procurement_uom/) | 10.0.1.0.0 | Glue module for stock_orderpoint_uom and stock_orderpoint_manual_procurement
[stock_orderpoint_uom](stock_orderpoint_uom/) | 10.0.1.0.1 | Allows to create procurement orders in the UoM indicated in the orderpoint
[stock_product_location_sorted_by_qty](stock_product_location_sorted_by_qty/) | 10.0.1.0.0 | In the update wizard of quantities for a product, sort the stock location by quantity
[stock_putaway_product](stock_putaway_product/) | 10.0.1.1.0 | Set a product location and put-away strategy per product
[stock_quant_manual_assign](stock_quant_manual_assign/) | 10.0.1.0.1 | Stock - Manual Quant Assignment
[stock_quant_merge](stock_quant_merge/) | 10.0.1.0.1 | Stock - Quant merge
[stock_quant_reserved_qty_uom](stock_quant_reserved_qty_uom/) | 10.0.1.0.0 | Stock Quant Reserved Qty UoM
[stock_removal_location_by_priority](stock_removal_location_by_priority/) | 10.0.1.0.0 | Establish a removal priority on stock locations.
[stock_reserve](stock_reserve/) | 10.0.1.0.0 | Stock reservations on products
[stock_valuation_account_manual_adjustment](stock_valuation_account_manual_adjustment/) | 10.0.1.0.0 | Shows in the product inventory stock value and the accounting value and allows to reconcile them
[stock_warehouse_orderpoint_stock_info](stock_warehouse_orderpoint_stock_info/) | 10.0.1.0.0 | Stock Warehouse Orderpoint Stock Info
[stock_warehouse_orderpoint_stock_info_unreserved](stock_warehouse_orderpoint_stock_info_unreserved/) | 10.0.1.0.0 | Stock Warehouse Orderpoint Stock Info Unreserved


Unported addons
---------------
addon | version | summary
--- | --- | ---
[base_product_merge](base_product_merge/) | 1.0 (unported) | Base Products Merge
[configurable_stock_level](configurable_stock_level/) | 0.1 (unported) | name
[partner_location_auto_create](partner_location_auto_create/) | 0.1 (unported) | Partner Location Auto Create
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
