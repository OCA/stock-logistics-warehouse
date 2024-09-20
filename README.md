
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-warehouse&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-warehouse/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-warehouse)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-warehouse-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-warehouse-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Odoo Stock Logistics Warehouse

This project aim to deal with modules related to the management of warehouses. You'll find modules that:

 - Ease inventory by adding various possibilities
 - Move all product from one location to another
 - Manage the product catalog (merge them,..)

Please don't hesitate to suggest one of your module to this project. Also, you may want to have a look on those other projects here:

 - https://github.com/OCA/stock-logistics-tracking
 - https://github.com/OCA/stock-logistics-barcode
 - https://github.com/OCA/stock-logistics-workflow

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_product](account_move_line_product/) | 13.0.1.0.0 |  | Displays the product in the journal entries and items
[account_move_line_stock_info](account_move_line_stock_info/) | 13.0.1.2.0 |  | Account Move Line Stock Info
[procurement_auto_create_group](procurement_auto_create_group/) | 13.0.1.3.0 |  | Allows to configure the system to propose automatically new procurement groups during the procurement run.
[product_quantity_update_force_inventory](product_quantity_update_force_inventory/) | 13.0.1.0.0 |  | Product Quantity Update Force Inventory
[sale_automatic_workflow_reserve_sale_stock](sale_automatic_workflow_reserve_sale_stock/) | 13.0.1.0.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Sale Automatic Workflow: Reserve Sale stock
[sale_stock_available_info_popup](sale_stock_available_info_popup/) | 13.0.1.0.3 |  | Adds an 'Available to promise' quantity to the popover shown in sale order line that display stock info of the product
[scrap_reason_code](scrap_reason_code/) | 13.0.1.1.1 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Reason code for scrapping
[stock_account_change_qty_reason](stock_account_change_qty_reason/) | 13.0.1.0.0 |  | Stock Account Change Quantity Reason
[stock_account_inventory_discrepancy](stock_account_inventory_discrepancy/) | 13.0.1.0.0 |  | Adds the capability to show the value discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_archive_constraint](stock_archive_constraint/) | 13.0.1.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock archive constraint
[stock_available](stock_available/) | 13.0.1.0.2 |  | Stock available to promise
[stock_available_immediately](stock_available_immediately/) | 13.0.1.0.0 |  | Ignore planned receptions in quantity available to promise
[stock_available_mrp](stock_available_mrp/) | 13.0.2.0.0 |  | Consider the production potential is available to promise
[stock_available_unreserved](stock_available_unreserved/) | 13.0.1.0.2 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Quantity of stock available for immediate use
[stock_change_qty_reason](stock_change_qty_reason/) | 13.0.2.0.0 |  | Stock Quantity Change Reason
[stock_cubiscan](stock_cubiscan/) | 13.0.1.1.1 |  | Implement inteface with Cubiscan devices for packaging
[stock_cycle_count](stock_cycle_count/) | 13.0.1.2.1 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Adds the capability to schedule cycle counts in a warehouse through different rules defined by the user.
[stock_demand_estimate](stock_demand_estimate/) | 13.0.1.2.0 |  | Allows to create demand estimates.
[stock_demand_estimate_matrix](stock_demand_estimate_matrix/) | 13.0.1.2.0 |  | Allows to create demand estimates.
[stock_helper](stock_helper/) | 13.0.1.1.0 |  | Add methods shared between various stock modules
[stock_inventory_chatter](stock_inventory_chatter/) | 13.0.1.0.0 |  | Log changes being done in Inventory Adjustments
[stock_inventory_cost_info](stock_inventory_cost_info/) | 13.0.1.0.0 |  | Shows the cost of the inventory adjustments
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 13.0.1.1.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_exclude_sublocation](stock_inventory_exclude_sublocation/) | 13.0.1.0.1 |  | Allow to perform inventories of a location without including its child locations.
[stock_inventory_include_exhausted](stock_inventory_include_exhausted/) | 13.0.1.2.0 |  | It includes the option for adding products exhausted on the inventories.
[stock_inventory_justification](stock_inventory_justification/) | 13.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | This module allows to set justification on inventories
[stock_inventory_line_open](stock_inventory_line_open/) | 13.0.1.0.0 |  | Open inventory lines on validated inventory adjustments
[stock_inventory_lockdown](stock_inventory_lockdown/) | 13.0.1.0.2 |  | Lock down stock locations during inventories.
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 13.0.1.0.1 |  | More filters for inventory adjustments
[stock_location_bin_name](stock_location_bin_name/) | 13.0.1.0.0 |  | Compute bin stock location name automatically
[stock_location_children](stock_location_children/) | 13.0.1.0.1 |  | Add relation between stock location and all its children
[stock_location_last_inventory_date](stock_location_last_inventory_date/) | 13.0.1.0.1 |  | Show the last inventory date for a leaf location
[stock_location_lockdown](stock_location_lockdown/) | 13.0.1.0.1 |  | Prevent to add stock on locked locations
[stock_location_position](stock_location_position/) | 13.0.1.0.0 |  | Add coordinate attributes on stock location.
[stock_location_route_description](stock_location_route_description/) | 13.0.1.0.1 |  | Add description field on stock routes.
[stock_location_tray](stock_location_tray/) | 13.0.1.0.2 |  | Organize a location as a matrix of cells
[stock_location_zone](stock_location_zone/) | 13.0.1.0.0 |  | Classify locations with zones.
[stock_lot_filter_available](stock_lot_filter_available/) | 13.0.2.0.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Allow to filter lots by available on stock
[stock_measuring_device](stock_measuring_device/) | 13.0.1.1.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) | Implement a common interface for measuring and weighing devices
[stock_measuring_device_zippcube](stock_measuring_device_zippcube/) | 13.0.1.1.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) | Implement interface with Bosche Zippcube devicesfor packaging measurement
[stock_move_auto_assign](stock_move_auto_assign/) | 13.0.1.1.0 |  | Try to reserve moves when goods enter in a location
[stock_move_common_dest](stock_move_common_dest/) | 13.0.1.1.0 |  | Adds field for common destination moves
[stock_move_location](stock_move_location/) | 13.0.1.2.0 |  | This module allows to move all stock in a stock location to an other one.
[stock_move_packaging_qty](stock_move_packaging_qty/) | 13.0.1.1.1 |  | Add packaging fields in the stock moves
[stock_mts_mto_rule](stock_mts_mto_rule/) | 13.0.1.3.0 |  | Add a MTS+MTO route
[stock_orderpoint_generator](stock_orderpoint_generator/) | 13.0.2.0.0 |  | Mass configuration of stock order points
[stock_orderpoint_manual_procurement](stock_orderpoint_manual_procurement/) | 13.0.1.0.1 |  | Allows to create procurement orders from orderpoints instead of relying only on the scheduler.
[stock_orderpoint_manual_procurement_uom](stock_orderpoint_manual_procurement_uom/) | 13.0.1.0.0 |  | Glue module for stock_orderpoint_uom and stock_orderpoint_manual_procurement
[stock_orderpoint_move_link](stock_orderpoint_move_link/) | 13.0.1.0.0 |  | Link Reordering rules to stock moves
[stock_orderpoint_purchase_link](stock_orderpoint_purchase_link/) | 13.0.1.1.0 |  | Link Reordering rules to purchase orders
[stock_orderpoint_route](stock_orderpoint_route/) | 13.0.1.0.0 |  | Allows to force a route to be used when procuring from orderpoints
[stock_orderpoint_uom](stock_orderpoint_uom/) | 13.0.1.0.0 |  | Allows to create procurement orders in the UoM indicated in the orderpoint
[stock_packaging_calculator](stock_packaging_calculator/) | 13.0.1.9.1 |  | Compute product quantity to pick by packaging
[stock_packaging_calculator_packaging_type](stock_packaging_calculator_packaging_type/) | 13.0.1.1.0 |  | Glue module for packaging type
[stock_picking_completion_info](stock_picking_completion_info/) | 13.0.1.1.0 |  | Display on current document completion information according to next operations
[stock_picking_consolidation_priority](stock_picking_consolidation_priority/) | 13.0.1.0.0 |  | Raise priority of all transfers for a chain when started
[stock_picking_orig_dest_link](stock_picking_orig_dest_link/) | 13.0.1.0.0 |  | This addon link the pickings with their respective Origin and Destination Pickings.
[stock_picking_package_grouped](stock_picking_package_grouped/) | 13.0.1.0.1 |  | Allow create package (put in pack) from pickings depending on grouping criteria.
[stock_picking_procure_method](stock_picking_procure_method/) | 13.0.1.0.0 |  | Allows to force the procurement method from the picking
[stock_picking_show_linked](stock_picking_show_linked/) | 13.0.1.0.2 |  | This addon allows to easily access related pickings (in the case of chained routes) through a button in the parent picking view.
[stock_product_qty_by_packaging](stock_product_qty_by_packaging/) | 13.0.1.1.0 |  | Compute product quantity to pick by packaging
[stock_production_lot_quantity_tree](stock_production_lot_quantity_tree/) | 13.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Allows to display product quantity field on production lot tree view
[stock_pull_list](stock_pull_list/) | 13.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | The pull list checks the stock situation and calculates needed quantities.
[stock_putaway_product_template](stock_putaway_product_template/) | 13.0.1.1.0 | [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Add product template in putaway strategies from the product view
[stock_quant_expiration_date_tree](stock_quant_expiration_date_tree/) | 13.0.1.0.0 | [![Manuel Calero](https://github.com/Manuel Calero.png?size=30px)](https://github.com/Manuel Calero) | Allows to display expirations dates on stock quant tree view
[stock_quant_manual_assign](stock_quant_manual_assign/) | 13.0.1.2.0 |  | Stock - Manual Quant Assignment
[stock_quant_reservation_info](stock_quant_reservation_info/) | 13.0.1.0.0 |  | Allows to see the reserved info of Products
[stock_quant_reservation_info_mrp](stock_quant_reservation_info_mrp/) | 13.0.1.0.0 |  | Allows to see the manufacturing order related to the reserved info of Products
[stock_quant_view_reservation](stock_quant_view_reservation/) | 13.0.1.0.0 |  | Allows to see details of reservations on a quant
[stock_removal_location_by_priority](stock_removal_location_by_priority/) | 13.0.1.0.0 |  | Establish a removal priority on stock locations.
[stock_request](stock_request/) | 13.0.1.7.3 |  | Internal request for stock
[stock_request_analytic](stock_request_analytic/) | 13.0.1.0.0 |  | Internal request for stock
[stock_request_direction](stock_request_direction/) | 13.0.1.0.1 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | From or to your warehouse?
[stock_request_kanban](stock_request_kanban/) | 13.0.1.0.1 |  | Adds a stock request order, and takes stock requests as lines
[stock_request_mrp](stock_request_mrp/) | 13.0.1.0.0 |  | Manufacturing request for stock
[stock_request_picking_type](stock_request_picking_type/) | 13.0.1.1.0 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Add Stock Requests to the Inventory App
[stock_request_purchase](stock_request_purchase/) | 13.0.1.0.1 |  | Internal request for stock
[stock_request_submit](stock_request_submit/) | 13.0.1.0.0 |  | Add submit state on Stock Requests
[stock_request_tier_validation](stock_request_tier_validation/) | 13.0.1.0.0 |  | Extends the functionality of Stock Requests to support a tier validation process.
[stock_reserve](stock_reserve/) | 13.0.1.0.0 |  | Stock reservations on products
[stock_reserve_rule](stock_reserve_rule/) | 13.0.1.5.0 |  | Configure reservation rules by location
[stock_reserve_sale](stock_reserve_sale/) | 13.0.1.1.0 |  | Stock Reserve Sales
[stock_reserve_sale_mrp](stock_reserve_sale_mrp/) | 13.0.1.1.0 |  | Stock Reserve Sales MRP
[stock_secondary_unit](stock_secondary_unit/) | 13.0.2.1.1 |  | Get product quantities in a secondary unit
[stock_vertical_lift](stock_vertical_lift/) | 13.0.1.3.1 |  | Provides the core for integration with Vertical Lifts
[stock_vertical_lift_empty_tray_check](stock_vertical_lift_empty_tray_check/) | 13.0.1.1.0 |  | Checks if the tray is actually empty.
[stock_vertical_lift_kardex](stock_vertical_lift_kardex/) | 13.0.1.1.0 |  | Integrate with Kardex Remstar Vertical Lifts
[stock_vertical_lift_packaging_type](stock_vertical_lift_packaging_type/) | 13.0.1.0.0 |  | Provides integration with Vertical Lifts and packaging types
[stock_vertical_lift_qty_by_packaging](stock_vertical_lift_qty_by_packaging/) | 13.0.1.0.0 |  | Glue module for `stock_product_qty_by_packaging` and `stock_vertical_lift`.
[stock_vertical_lift_server_env](stock_vertical_lift_server_env/) | 13.0.1.0.0 |  | Server Environment layer for Vertical Lift
[stock_vertical_lift_storage_type](stock_vertical_lift_storage_type/) | 13.0.1.0.0 |  | Compatibility layer for storage types on vertical lifts
[stock_warehouse_calendar](stock_warehouse_calendar/) | 13.0.1.0.1 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) | Adds a calendar to the Warehouse
[stock_warehouse_orderpoint_stock_info](stock_warehouse_orderpoint_stock_info/) | 13.0.1.0.0 |  | Stock Warehouse Orderpoint Stock Info
[stock_warehouse_orderpoint_stock_info_unreserved](stock_warehouse_orderpoint_stock_info_unreserved/) | 13.0.1.0.0 |  | Stock Warehouse Orderpoint Stock Info Unreserved

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
