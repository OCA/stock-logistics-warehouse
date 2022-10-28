
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-warehouse&target_branch=11.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml/badge.svg?branch=11.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml?query=branch%3A11.0)
[![Build Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml/badge.svg?branch=11.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml?query=branch%3A11.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-warehouse/branch/11.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-warehouse)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-warehouse-11-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-warehouse-11-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Odoo Warehouse Management Addons

None

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_product](account_move_line_product/) | 11.0.1.0.2 |  | Displays the product in the journal entries and items
[account_move_line_stock_info](account_move_line_stock_info/) | 11.0.1.0.0 |  | Account Move Line Stock Move
[packaging_uom](packaging_uom/) | 11.0.1.0.1 |  | Use uom in package
[procurement_auto_create_group](procurement_auto_create_group/) | 11.0.1.0.0 |  | Allows to configure the system to propose automatically new procurement groups in procurement orders.
[push_rule_auto_create_group](push_rule_auto_create_group/) | 11.0.1.0.1 |  | Allows to configure the system to propose automatically new procurement groups in applying push rules.
[scrap_reason_code](scrap_reason_code/) | 11.0.1.0.0 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Reason code for scrapping
[stock_account_change_qty_reason](stock_account_change_qty_reason/) | 11.0.1.0.0 |  | Stock Account Change Quantity Reason
[stock_account_internal_move](stock_account_internal_move/) | 11.0.1.0.0 | [![arkostyuk](https://github.com/arkostyuk.png?size=30px)](https://github.com/arkostyuk) [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Allows tracking moves between internal locations via accounts.
[stock_account_inventory_force_date](stock_account_inventory_force_date/) | 11.0.1.0.0 |  | Force the inventory adjustments to a date in the past.
[stock_available](stock_available/) | 11.0.1.1.1 |  | Stock available to promise
[stock_available_global](stock_available_global/) | 11.0.1.0.1 |  | Stock available global (All companies)
[stock_available_immediately](stock_available_immediately/) | 11.0.1.0.1 |  | Ignore planned receptions in quantity available to promise
[stock_available_mrp](stock_available_mrp/) | 11.0.1.1.0 |  | Consider the production potential is available to promise
[stock_available_unreserved](stock_available_unreserved/) | 11.0.1.0.0 |  | Quantity of stock available for immediate use
[stock_change_qty_reason](stock_change_qty_reason/) | 11.0.2.0.0 |  | Stock Quantity Change Reason
[stock_cycle_count](stock_cycle_count/) | 11.0.1.0.2 | [![lreficent](https://github.com/lreficent.png?size=30px)](https://github.com/lreficent) | Adds the capability to schedule cycle counts in a warehouse through different rules defined by the user.
[stock_demand_estimate](stock_demand_estimate/) | 11.0.1.2.0 |  | Allows to create demand estimates.
[stock_inventory_chatter](stock_inventory_chatter/) | 11.0.1.0.0 |  | Log changes being done in Inventory Adjustments
[stock_inventory_cost_info](stock_inventory_cost_info/) | 11.0.1.1.0 |  | Shows the cost of the inventory adjustments
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 11.0.1.0.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_exclude_sublocation](stock_inventory_exclude_sublocation/) | 11.0.2.0.1 |  | Allow to perform inventories of a location without including its child locations.
[stock_inventory_lockdown](stock_inventory_lockdown/) | 11.0.1.0.2 |  | Lock down stock locations during inventories.
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 11.0.1.0.1 |  | More filters for inventory adjustments
[stock_inventory_verification_request](stock_inventory_verification_request/) | 11.0.1.0.1 | [![lreficent](https://github.com/lreficent.png?size=30px)](https://github.com/lreficent) | Adds the capability to request a Slot Verification when a inventory is Pending to Approve
[stock_inventory_virtual_location](stock_inventory_virtual_location/) | 11.0.1.0.0 |  | Allows to change the virtual location in inventory adjustments.
[stock_inventory_virtual_location_change_qty_reason](stock_inventory_virtual_location_change_qty_reason/) | 11.0.1.0.0 |  | Glue module
[stock_move_location](stock_move_location/) | 11.0.2.1.0 |  | This module allows to move all stock in a stock location to an other one.
[stock_mts_mto_rule](stock_mts_mto_rule/) | 11.0.1.0.1 |  | Add a MTS+MTO route
[stock_orderpoint_generator](stock_orderpoint_generator/) | 11.0.2.0.0 |  | Mass configuration of stock order points
[stock_orderpoint_manual_procurement](stock_orderpoint_manual_procurement/) | 11.0.1.1.1 |  | Allows to create procurement orders from orderpoints instead of relying only on the scheduler.
[stock_orderpoint_manual_procurement_uom](stock_orderpoint_manual_procurement_uom/) | 11.0.1.0.0 |  | Glue module for stock_orderpoint_uom and stock_orderpoint_manual_procurement
[stock_orderpoint_move_link](stock_orderpoint_move_link/) | 11.0.1.1.1 |  | Link Reordering rules to stock moves
[stock_orderpoint_mrp_link](stock_orderpoint_mrp_link/) | 11.0.1.1.0 |  | Link Reordering rules to purchase orders
[stock_orderpoint_procure_location](stock_orderpoint_procure_location/) | 11.0.1.0.0 |  | Allows to create procurement orders in a different locationthe orderpoint
[stock_orderpoint_purchase_link](stock_orderpoint_purchase_link/) | 11.0.1.1.0 |  | Link Reordering rules to purchase orders
[stock_orderpoint_uom](stock_orderpoint_uom/) | 11.0.1.0.0 |  | Allows to create procurement orders in the UoM indicated in the orderpoint
[stock_picking_procure_method](stock_picking_procure_method/) | 11.0.1.0.0 |  | Allows to force the procurement method from the picking
[stock_production_lot_expiry_state](stock_production_lot_expiry_state/) | 11.0.1.0.0 | [![osimallen](https://github.com/osimallen.png?size=30px)](https://github.com/osimallen) [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Add a state field to expiring lot/SN
[stock_putaway_method](stock_putaway_method/) | 11.0.1.0.1 |  | Add the putaway strategy method back, removed from the stock module in Odoo 11
[stock_putaway_product](stock_putaway_product/) | 11.0.1.0.3 |  | Set a product location and put-away strategy per product
[stock_putaway_same_location](stock_putaway_same_location/) | 11.0.1.0.0 |  | Adds a new putaway strategy at product receivals
[stock_quant_manual_assign](stock_quant_manual_assign/) | 11.0.1.0.1 |  | Stock - Manual Quant Assignment
[stock_removal_location_by_priority](stock_removal_location_by_priority/) | 11.0.1.0.0 |  | Establish a removal priority on stock locations.
[stock_request](stock_request/) | 11.0.3.4.7 |  | Internal request for stock
[stock_request_analytic](stock_request_analytic/) | 11.0.2.0.3 |  | Internal request for stock
[stock_request_employee](stock_request_employee/) | 11.0.1.0.0 |  | Deliver Stock requests directly to employees
[stock_request_kanban](stock_request_kanban/) | 11.0.1.2.0 |  | Adds a stock request order, and takes stock requests as lines
[stock_request_purchase](stock_request_purchase/) | 11.0.2.2.2 |  | Internal request for stock
[stock_request_purchase_analytic](stock_request_purchase_analytic/) | 11.0.1.0.2 |  | Passes the analytic account from the stock request to the purchase order
[stock_request_tier_validation](stock_request_tier_validation/) | 11.0.1.2.0 |  | Extends the functionality of Stock Requests to support a tier validation process.
[stock_secondary_unit](stock_secondary_unit/) | 11.0.1.0.4 |  | Get product quantities in a secondary unit
[stock_warehouse_calendar](stock_warehouse_calendar/) | 11.0.1.0.1 | [![jbeficent](https://github.com/jbeficent.png?size=30px)](https://github.com/jbeficent) | Adds a calendar to the Warehouse
[stock_warehouse_orderpoint_stock_info](stock_warehouse_orderpoint_stock_info/) | 11.0.1.0.0 |  | Stock Warehouse Orderpoint Stock Info
[stock_warehouse_orderpoint_stock_info_unreserved](stock_warehouse_orderpoint_stock_info_unreserved/) | 11.0.1.0.0 |  | Stock Warehouse Orderpoint Stock Info Unreserved

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
