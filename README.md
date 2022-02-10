[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/153/14.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-stock-logistics-warehouse-153)
[![Build Status](https://travis-ci.com/OCA/stock-logistics-warehouse.svg?branch=14.0)](https://travis-ci.com/OCA/stock-logistics-warehouse)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-warehouse/branch/14.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-warehouse)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-warehouse-14-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-warehouse-14-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# stock-logistics-warehouse

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_product](account_move_line_product/) | 14.0.1.0.0 |  | Displays the product in the journal entries and items
[account_move_line_stock_info](account_move_line_stock_info/) | 14.0.1.0.0 |  | Account Move Line Stock Info
[procurement_auto_create_group](procurement_auto_create_group/) | 14.0.1.2.0 |  | Allows to configure the system to propose automatically new procurement groups during the procurement run.
[product_quantity_update_force_inventory](product_quantity_update_force_inventory/) | 14.0.1.0.1 |  | Product Quantity Update Force Inventory
[scrap_reason_code](scrap_reason_code/) | 14.0.1.0.0 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Reason code for scrapping
[stock_archive_constraint](stock_archive_constraint/) | 14.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock archive constraint
[stock_available](stock_available/) | 14.0.1.0.3 |  | Stock available to promise
[stock_available_immediately](stock_available_immediately/) | 14.0.1.0.0 |  | Ignore planned receptions in quantity available to promise
[stock_available_mrp](stock_available_mrp/) | 14.0.1.0.3 |  | Consider the production potential is available to promise
[stock_available_unreserved](stock_available_unreserved/) | 14.0.1.0.2 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Quantity of stock available for immediate use
[stock_change_qty_reason](stock_change_qty_reason/) | 14.0.1.0.1 |  | Stock Quantity Change Reason
[stock_cycle_count](stock_cycle_count/) | 14.0.1.2.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Adds the capability to schedule cycle counts in a warehouse through different rules defined by the user.
[stock_demand_estimate](stock_demand_estimate/) | 14.0.1.1.0 |  | Allows to create demand estimates.
[stock_demand_estimate_matrix](stock_demand_estimate_matrix/) | 14.0.1.0.0 |  | Allows to create demand estimates.
[stock_free_quantity](stock_free_quantity/) | 14.0.1.0.0 |  | Stock Free Quantity
[stock_generate_putaway_from_inventory](stock_generate_putaway_from_inventory/) | 14.0.1.0.0 | [![pierrickbrun](https://github.com/pierrickbrun.png?size=30px)](https://github.com/pierrickbrun) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) | Generate Putaway locations per Product deduced from Inventory
[stock_helper](stock_helper/) | 14.0.1.0.0 |  | Add methods shared between various stock modules
[stock_inventory_cost_info](stock_inventory_cost_info/) | 14.0.1.0.0 |  | Shows the cost of the inventory adjustments
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 14.0.1.1.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_exclude_sublocation](stock_inventory_exclude_sublocation/) | 14.0.1.0.1 |  | Allow to perform inventories of a location without including its child locations.
[stock_inventory_line_product_cost](stock_inventory_line_product_cost/) | 14.0.1.0.0 |  | Stock Adjustment Cost
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 14.0.1.0.0 |  | More filters for inventory adjustments
[stock_inventory_preparation_filter_pos](stock_inventory_preparation_filter_pos/) | 14.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Add POS category filter on inventory adjustments
[stock_location_bin_name](stock_location_bin_name/) | 14.0.1.0.0 |  | Compute bin stock location name automatically
[stock_location_children](stock_location_children/) | 14.0.1.0.0 |  | Add relation between stock location and all its children
[stock_location_empty](stock_location_empty/) | 14.0.1.0.0 |  | Adds a filter for empty stock location
[stock_location_last_inventory_date](stock_location_last_inventory_date/) | 14.0.1.0.0 |  | Show the last inventory date for a leaf location
[stock_location_lockdown](stock_location_lockdown/) | 14.0.1.0.0 |  | Prevent to add stock on locked locations
[stock_location_position](stock_location_position/) | 14.0.1.0.0 |  | Add coordinate attributes on stock location.
[stock_location_tray](stock_location_tray/) | 14.0.1.1.2 |  | Organize a location as a matrix of cells
[stock_location_warehouse](stock_location_warehouse/) | 14.0.1.0.0 |  | Warehouse associated with a location
[stock_location_zone](stock_location_zone/) | 14.0.1.0.0 |  | Classify locations with zones.
[stock_measuring_device](stock_measuring_device/) | 14.0.1.0.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) | Implement a common interface for measuring and weighing devices
[stock_measuring_device_zippcube](stock_measuring_device_zippcube/) | 14.0.1.0.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) | Implement interface with Bosche Zippcube devicesfor packaging measurement
[stock_move_auto_assign](stock_move_auto_assign/) | 14.0.1.0.0 |  | Try to reserve moves when goods enter in a location
[stock_move_common_dest](stock_move_common_dest/) | 14.0.1.0.0 |  | Adds field for common destination moves
[stock_move_location](stock_move_location/) | 14.0.1.1.0 |  | This module allows to move all stock in a stock location to an other one.
[stock_mts_mto_rule](stock_mts_mto_rule/) | 14.0.1.0.0 |  | Add a MTS+MTO route
[stock_orderpoint_manual_procurement](stock_orderpoint_manual_procurement/) | 14.0.1.0.2 |  | Allows to create procurement orders from orderpoints instead of relying only on the scheduler.
[stock_orderpoint_manual_procurement_uom](stock_orderpoint_manual_procurement_uom/) | 14.0.1.0.1 |  | Glue module for stock_orderpoint_uom and stock_orderpoint_manual_procurement
[stock_orderpoint_move_link](stock_orderpoint_move_link/) | 14.0.1.0.2 |  | Link Reordering rules to stock moves
[stock_orderpoint_origin](stock_orderpoint_origin/) | 14.0.1.0.0 |  | Link Purchase Orders to the replenishment demand Sales Orders
[stock_orderpoint_origin_mrp_link](stock_orderpoint_origin_mrp_link/) | 14.0.1.0.0 |  | Link Purchase Orders to the replenishment demand MOs
[stock_orderpoint_purchase_link](stock_orderpoint_purchase_link/) | 14.0.1.0.0 |  | Link Reordering rules to purchase orders
[stock_orderpoint_route](stock_orderpoint_route/) | 14.0.1.1.0 |  | Allows to force a route to be used when procuring from orderpoints
[stock_orderpoint_uom](stock_orderpoint_uom/) | 14.0.1.0.0 |  | Allows to create procurement orders in the UoM indicated in the orderpoint
[stock_packaging_calculator](stock_packaging_calculator/) | 14.0.1.1.0 |  | Compute product quantity to pick by packaging
[stock_packaging_calculator_packaging_type](stock_packaging_calculator_packaging_type/) | 14.0.1.0.0 |  | Glue module for packaging type
[stock_picking_cancel_confirm](stock_picking_cancel_confirm/) | 14.0.1.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Stock Picking Cancel Confirm
[stock_product_qty_by_packaging](stock_product_qty_by_packaging/) | 14.0.1.0.0 |  | Compute product quantity to pick by packaging
[stock_pull_list](stock_pull_list/) | 14.0.1.1.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | The pull list checks the stock situation and calculates needed quantities.
[stock_putaway_method](stock_putaway_method/) | 14.0.1.0.0 | [![asaunier](https://github.com/asaunier.png?size=30px)](https://github.com/asaunier) | Add the putaway strategy method back, removed from the stock module in Odoo 12
[stock_putaway_product_template](stock_putaway_product_template/) | 14.0.1.1.0 | [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Add product template in putaway strategies from the product view
[stock_quant_manual_assign](stock_quant_manual_assign/) | 14.0.1.1.0 |  | Stock - Manual Quant Assignment
[stock_request](stock_request/) | 14.0.1.0.6 |  | Internal request for stock
[stock_request_analytic](stock_request_analytic/) | 14.0.1.0.2 |  | Internal request for stock
[stock_request_picking_type](stock_request_picking_type/) | 14.0.1.0.0 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Add Stock Requests to the Inventory App
[stock_request_purchase](stock_request_purchase/) | 14.0.1.0.0 |  | Internal request for stock
[stock_request_submit](stock_request_submit/) | 14.0.1.0.0 |  | Add submit state on Stock Requests
[stock_request_tier_validation](stock_request_tier_validation/) | 14.0.1.0.0 |  | Extends the functionality of Stock Requests to support a tier validation process.
[stock_reserve_rule](stock_reserve_rule/) | 14.0.1.1.0 |  | Configure reservation rules by location
[stock_search_supplierinfo_code](stock_search_supplierinfo_code/) | 14.0.1.0.0 |  | Allows to search for picking from supplierinfo code
[stock_secondary_unit](stock_secondary_unit/) | 14.0.1.0.1 |  | Get product quantities in a secondary unit
[stock_vertical_lift](stock_vertical_lift/) | 14.0.1.1.1 |  | Provides the core for integration with Vertical Lifts
[stock_vertical_lift_empty_tray_check](stock_vertical_lift_empty_tray_check/) | 14.0.1.0.0 |  | Checks if the tray is actually empty.
[stock_vertical_lift_kardex](stock_vertical_lift_kardex/) | 14.0.1.1.0 |  | Integrate with Kardex Remstar Vertical Lifts
[stock_vertical_lift_packaging_type](stock_vertical_lift_packaging_type/) | 14.0.1.0.0 |  | Provides integration with Vertical Lifts and packaging types
[stock_vertical_lift_qty_by_packaging](stock_vertical_lift_qty_by_packaging/) | 14.0.1.0.0 |  | Glue module for `stock_product_qty_by_packaging` and `stock_vertical_lift`.
[stock_vertical_lift_server_env](stock_vertical_lift_server_env/) | 14.0.1.0.0 |  | Server Environment layer for Vertical Lift
[stock_vertical_lift_storage_type](stock_vertical_lift_storage_type/) | 14.0.1.0.0 |  | Compatibility layer for storage types on vertical lifts
[stock_warehouse_calendar](stock_warehouse_calendar/) | 14.0.1.0.1 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) | Adds a calendar to the Warehouse

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
