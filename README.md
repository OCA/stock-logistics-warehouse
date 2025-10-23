
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-warehouse&target_branch=18.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml/badge.svg?branch=18.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml?query=branch%3A18.0)
[![Build Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml/badge.svg?branch=18.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml?query=branch%3A18.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-warehouse/branch/18.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-warehouse)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-warehouse-18-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-warehouse-18-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Stock Warehouse

Extend the stock related models (warehouse, location, picking, move...) but without impact flows and processes. It's mainly adding fields or buttons.

Are you looking for modules related to logistics? Or would like to contribute
to? There are many repositories with specific purposes. Have a look at this
[README](https://github.com/OCA/wms/blob/18.0/README.md).

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_stock_info](account_move_line_stock_info/) | 18.0.1.0.0 |  | Account Move Line Stock Info
[procurement_auto_create_group](procurement_auto_create_group/) | 18.0.1.0.1 |  | Allows to configure the system to propose automatically new procurement groups during the procurement run.
[product_route_profile](product_route_profile/) | 18.0.1.0.0 | <a href='https://github.com/Kev-Roche'><img src='https://github.com/Kev-Roche.png' width='32' height='32' style='border-radius:50%;' alt='Kev-Roche'/></a> | Add Route profile concept on product
[stock_archive_constraint](stock_archive_constraint/) | 18.0.1.0.0 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Stock archive constraint
[stock_change_qty_reason](stock_change_qty_reason/) | 18.0.1.0.0 |  | Stock Quantity Change Reason
[stock_cycle_count](stock_cycle_count/) | 18.0.1.0.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Adds the capability to schedule cycle counts in a warehouse through different rules defined by the user.
[stock_demand_estimate](stock_demand_estimate/) | 18.0.1.0.0 |  | Allows to create demand estimates.
[stock_demand_estimate_matrix](stock_demand_estimate_matrix/) | 18.0.1.0.0 |  | Allows to create demand estimates.
[stock_inventory](stock_inventory/) | 18.0.1.1.0 |  | Allows to do an easier follow up of the Inventory Adjustments
[stock_inventory_count_to_zero](stock_inventory_count_to_zero/) | 18.0.1.0.0 |  | Request an inventory count filling the quantities to zero as default
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 18.0.1.1.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_lockdown](stock_inventory_lockdown/) | 18.0.1.0.0 |  | Lock down stock locations during inventories.
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 18.0.1.0.0 |  | More filters for inventory adjustments
[stock_inventory_verification_request](stock_inventory_verification_request/) | 18.0.1.1.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Adds the capability to request a Slot Verification when a inventory is Pending to Approve
[stock_location_bin_name](stock_location_bin_name/) | 18.0.1.0.1 |  | Compute bin stock location name automatically
[stock_location_children](stock_location_children/) | 18.0.1.0.0 |  | Add relation between stock location and all its children
[stock_location_empty](stock_location_empty/) | 18.0.1.0.0 |  | Adds a filter for empty stock location
[stock_location_fill_state](stock_location_fill_state/) | 18.0.1.0.0 | <a href='https://github.com/rousseldenis'><img src='https://github.com/rousseldenis.png' width='32' height='32' style='border-radius:50%;' alt='rousseldenis'/></a> <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | This module allows to identify the fill state of stock locations
[stock_location_fill_state_qty_picked](stock_location_fill_state_qty_picked/) | 18.0.1.0.0 | <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> <a href='https://github.com/rousseldenis'><img src='https://github.com/rousseldenis.png' width='32' height='32' style='border-radius:50%;' alt='rousseldenis'/></a> | Glue module between stock_location_fill_state and stock_move_line_qty_picked
[stock_location_is_sublocation](stock_location_is_sublocation/) | 18.0.1.0.0 |  | Add method to check stock location is sublocation
[stock_location_lockdown](stock_location_lockdown/) | 18.0.1.0.0 |  | Prevent to add stock on locked locations
[stock_location_pending_move](stock_location_pending_move/) | 18.0.1.0.0 | <a href='https://github.com/rousseldenis'><img src='https://github.com/rousseldenis.png' width='32' height='32' style='border-radius:50%;' alt='rousseldenis'/></a> <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | This module allows to show pending stock moves (outgoing and incoming) on a stock location
[stock_location_position](stock_location_position/) | 18.0.1.0.0 |  | Add coordinate attributes on stock location.
[stock_location_tray](stock_location_tray/) | 18.0.1.0.0 |  | Organize a location as a matrix of cells
[stock_location_zone](stock_location_zone/) | 18.0.1.0.0 |  | Classify locations with zones.
[stock_move_common_dest](stock_move_common_dest/) | 18.0.1.0.1 |  | Adds field for common destination moves
[stock_move_location](stock_move_location/) | 18.0.1.0.1 |  | This module allows to move all stock in a stock location to an other one.
[stock_move_location_purchase_uom](stock_move_location_purchase_uom/) | 18.0.1.0.0 |  | This module 'glues' the modules stock_move_location and stock_move_purchase_uom.
[stock_move_packaging_qty](stock_move_packaging_qty/) | 18.0.1.0.1 | <a href='https://github.com/yajo'><img src='https://github.com/yajo.png' width='32' height='32' style='border-radius:50%;' alt='yajo'/></a> <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> | Add packaging fields in the stock moves
[stock_move_purchase_uom](stock_move_purchase_uom/) | 18.0.1.1.0 |  | Allow to use the purchase UoM in a stock move
[stock_move_reset_quantity](stock_move_reset_quantity/) | 18.0.1.0.0 |  | Reset quantity to zero
[stock_package_type_volume](stock_package_type_volume/) | 18.0.1.0.0 |  | Compute volume of a package type
[stock_packaging_calculator](stock_packaging_calculator/) | 18.0.2.0.0 |  | Compute product quantity to pick by packaging
[stock_picking_completion_info](stock_picking_completion_info/) | 18.0.1.0.0 |  | Display on current document completion information according to next operations
[stock_picking_product_assortment](stock_picking_product_assortment/) | 18.0.1.0.0 | <a href='https://github.com/CarlosRoca13'><img src='https://github.com/CarlosRoca13.png' width='32' height='32' style='border-radius:50%;' alt='CarlosRoca13'/></a> | Stock Picking Product Assortment
[stock_picking_show_linked](stock_picking_show_linked/) | 18.0.1.0.0 |  | This addon allows to easily access related pickings (in the case of chained routes) through a button in the parent picking view.
[stock_picking_stage](stock_picking_stage/) | 18.0.1.0.0 | <a href='https://github.com/imlopes'><img src='https://github.com/imlopes.png' width='32' height='32' style='border-radius:50%;' alt='imlopes'/></a> | Stock Picking Stages
[stock_picking_supplier_ref](stock_picking_supplier_ref/) | 18.0.1.1.0 |  | Adds a supplier reference field inside supplier's pickings and allows search for this reference.
[stock_picking_volume](stock_picking_volume/) | 18.0.1.1.0 | <a href='https://github.com/lmignon'><img src='https://github.com/lmignon.png' width='32' height='32' style='border-radius:50%;' alt='lmignon'/></a> | Compute volume information on stock moves and pickings
[stock_picking_volume_packaging](stock_picking_volume_packaging/) | 18.0.1.0.0 |  | Use volume information on potential product packaging to compute the volume of a stock.move
[stock_product_qty_by_packaging](stock_product_qty_by_packaging/) | 18.0.1.0.1 |  | Compute product quantity to pick by packaging
[stock_putaway_product_template](stock_putaway_product_template/) | 18.0.1.0.1 | <a href='https://github.com/kevinkhao'><img src='https://github.com/kevinkhao.png' width='32' height='32' style='border-radius:50%;' alt='kevinkhao'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | Add product template in putaway strategies from the product view
[stock_quant_cost_info](stock_quant_cost_info/) | 18.0.1.0.0 |  | Shows the cost of the quants
[stock_quant_reservation_info](stock_quant_reservation_info/) | 18.0.1.0.0 |  | Allows to see the reserved info of Products
[stock_quant_reservation_info_mrp](stock_quant_reservation_info_mrp/) | 18.0.1.0.0 |  | Allows to see the manufacturing order related to the reserved info of Products
[stock_route_location_source](stock_route_location_source/) | 18.0.1.0.1 |  | Add method to get source location of Inventory Routes
[stock_route_mto](stock_route_mto/) | 18.0.1.0.0 | <a href='https://github.com/rousseldenis'><img src='https://github.com/rousseldenis.png' width='32' height='32' style='border-radius:50%;' alt='rousseldenis'/></a> <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Allows to identify MTO routes through a checkbox and availability to filter them.
[stock_secondary_unit](stock_secondary_unit/) | 18.0.1.0.0 |  | Get product quantities in a secondary unit
[stock_storage_category_capacity_name](stock_storage_category_capacity_name/) | 18.0.1.0.1 |  | Allows to have a better display name for Stock Storage Category Capacity model
[stock_vertical_lift](stock_vertical_lift/) | 18.0.1.2.3 |  | Provides the core for integration with Vertical Lifts
[stock_vertical_lift_packaging_level](stock_vertical_lift_packaging_level/) | 18.0.1.0.0 |  | Provides integration with Vertical Lifts and packaging levels
[stock_vertical_lift_qty_by_packaging](stock_vertical_lift_qty_by_packaging/) | 18.0.1.0.0 |  | Glue module for `stock_product_qty_by_packaging` and `stock_vertical_lift`.
[stock_vertical_lift_server_env](stock_vertical_lift_server_env/) | 18.0.1.0.0 |  | Server Environment layer for Vertical Lift
[stock_warehouse_calendar](stock_warehouse_calendar/) | 18.0.1.1.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> | Adds a calendar to the Warehouse
[stock_warehouse_out_pull](stock_warehouse_out_pull/) | 18.0.1.0.2 |  | Restore delivery pull rules as in Odoo <= 17.0
[stock_warehouse_resupply_route_push](stock_warehouse_resupply_route_push/) | 18.0.1.0.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Use push rules for resupply from other warehouse routes.

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
