
[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# stock-logistics-warehouse
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-warehouse&target_branch=15.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml/badge.svg?branch=15.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml?query=branch%3A15.0)
[![Build Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml/badge.svg?branch=15.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml?query=branch%3A15.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-warehouse/branch/15.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-warehouse)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-warehouse-15-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-warehouse-15-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

<<<<<<< before updating
# stock-logistics-warehouse

This project aim to deal with modules related to the management of warehouses. You'll find modules that:
=======
This project aim to deal with modules related to the management of warehouses. Youll find modules that:\n - Ease inventory by adding various possibilities - Move all product from one location to another - Manage the product catalog (merge them,..)
Please dont hesitate to suggest one of your module to this project. Also, you may want to have a look on those other projects here:
- https://github.com/OCA/stock-logistics-tracking - https://github.com/OCA/stock-logistics-barcode - https://github.com/OCA/stock-logistics-workflow
>>>>>>> after updating

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_product](account_move_line_product/) | 15.0.1.0.1 |  | Displays the product in the journal entries and items
[account_move_line_stock_info](account_move_line_stock_info/) | 15.0.1.1.0 |  | Account Move Line Stock Info
[base_product_merge](base_product_merge/) | 15.0.1.0.0 | <a href='https://github.com/JasminSForgeFlow'><img src='https://github.com/JasminSForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JasminSForgeFlow'/></a> | Merge duplicate products
[procurement_auto_create_group](procurement_auto_create_group/) | 15.0.1.0.0 |  | Allows to configure the system to propose automatically new procurement groups during the procurement run.
[product_route_profile](product_route_profile/) | 15.0.1.0.0 | <a href='https://github.com/Kev-Roche'><img src='https://github.com/Kev-Roche.png' width='32' height='32' style='border-radius:50%;' alt='Kev-Roche'/></a> | Add Route profile concept on product
[sale_stock_available_info_popup](sale_stock_available_info_popup/) | 15.0.1.0.0 |  | Adds an 'Available to promise' quantity to the popover shown in sale order line that display stock info of the product
[scrap_reason_code](scrap_reason_code/) | 15.0.1.1.0 | <a href='https://github.com/bodedra'><img src='https://github.com/bodedra.png' width='32' height='32' style='border-radius:50%;' alt='bodedra'/></a> | Reason code for scrapping
[stock_archive_constraint](stock_archive_constraint/) | 15.0.1.0.2 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Stock archive constraint
[stock_available](stock_available/) | 15.0.1.0.0 |  | Stock available to promise
[stock_available_immediately](stock_available_immediately/) | 15.0.1.0.0 |  | Ignore planned receptions in quantity available to promise
[stock_available_mrp](stock_available_mrp/) | 15.0.1.0.3 |  | Consider the production potential is available to promise
[stock_available_unreserved](stock_available_unreserved/) | 15.0.1.0.1 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Quantity of stock available for immediate use
[stock_change_qty_reason](stock_change_qty_reason/) | 15.0.1.0.0 |  | Stock Quantity Change Reason
[stock_cycle_count](stock_cycle_count/) | 15.0.2.2.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Adds the capability to schedule cycle counts in a warehouse through different rules defined by the user.
[stock_demand_estimate](stock_demand_estimate/) | 15.0.1.2.0 |  | Allows to create demand estimates.
[stock_demand_estimate_matrix](stock_demand_estimate_matrix/) | 15.0.1.2.0 |  | Allows to create demand estimates.
[stock_free_quantity](stock_free_quantity/) | 15.0.1.0.1 |  | Stock Free Quantity
[stock_helper](stock_helper/) | 15.0.1.0.0 |  | Add methods shared between various stock modules
[stock_inventory](stock_inventory/) | 15.0.2.5.1 |  | Allows to do an easier follow up of the Inventory Adjustments
[stock_inventory_count_to_zero](stock_inventory_count_to_zero/) | 15.0.1.0.0 |  | Request an inventory count filling the quantities to zero as default
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 15.0.1.1.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_lockdown](stock_inventory_lockdown/) | 15.0.1.0.1 |  | Lock down stock locations during inventories.
[stock_inventory_verification_request](stock_inventory_verification_request/) | 15.0.1.2.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Adds the capability to request a Slot Verification when a inventory is Pending to Approve
[stock_location_lockdown](stock_location_lockdown/) | 15.0.1.0.1 |  | Prevent to add stock on locked locations
[stock_location_position](stock_location_position/) | 15.0.1.0.0 |  | Add coordinate attributes on stock location.
[stock_location_route_description](stock_location_route_description/) | 15.0.1.0.0 |  | Add description field on stock routes.
[stock_lot_filter_available](stock_lot_filter_available/) | 15.0.1.0.1 | <a href='https://github.com/CarlosRoca13'><img src='https://github.com/CarlosRoca13.png' width='32' height='32' style='border-radius:50%;' alt='CarlosRoca13'/></a> | Allow to filter lots by available on stock
[stock_move_location](stock_move_location/) | 15.0.1.5.2 |  | This module allows to move all stock in a stock location to an other one.
[stock_move_location_purchase_uom](stock_move_location_purchase_uom/) | 15.0.1.0.0 |  | This module 'glues' the modules stock_move_location and stock_move_purchase_uom.
[stock_move_purchase_uom](stock_move_purchase_uom/) | 15.0.1.0.2 |  | Allow to use the purchase UoM in a stock move
[stock_mts_mto_rule](stock_mts_mto_rule/) | 15.0.1.0.1 |  | Add a MTS+MTO route
[stock_orderpoint_generator](stock_orderpoint_generator/) | 15.0.1.0.2 |  | Mass configuration of stock order points
[stock_orderpoint_move_link](stock_orderpoint_move_link/) | 15.0.1.0.1 |  | Link Reordering rules to stock moves
[stock_orderpoint_purchase_link](stock_orderpoint_purchase_link/) | 15.0.1.0.0 |  | Link Reordering rules to purchase orders
[stock_orderpoint_uom](stock_orderpoint_uom/) | 15.0.1.1.0 |  | Allows to create procurement orders in the UoM indicated in the orderpoint
[stock_packaging_calculator](stock_packaging_calculator/) | 15.0.1.0.0 |  | Compute product quantity to pick by packaging
[stock_picking_orig_dest_link](stock_picking_orig_dest_link/) | 15.0.1.0.0 |  | This addon link the pickings with their respective Origin and Destination Pickings.
[stock_picking_show_linked](stock_picking_show_linked/) | 15.0.1.0.0 |  | This addon allows to easily access related pickings (in the case of chained routes) through a button in the parent picking view.
[stock_procurement_group_hook](stock_procurement_group_hook/) | 15.0.1.0.0 |  | Adds Hook to Procurement Group run method.
[stock_putaway_product_template](stock_putaway_product_template/) | 15.0.1.1.0 | <a href='https://github.com/kevinkhao'><img src='https://github.com/kevinkhao.png' width='32' height='32' style='border-radius:50%;' alt='kevinkhao'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | Add product template in putaway strategies from the product view
[stock_quant_cost_info](stock_quant_cost_info/) | 15.0.1.1.1 |  | Shows the cost of the quants
[stock_quant_manual_assign](stock_quant_manual_assign/) | 15.0.1.2.1 |  | Stock - Manual Quant Assignment
[stock_quant_reservation_info](stock_quant_reservation_info/) | 15.0.1.0.1 |  | Allows to see the reserved info of Products
[stock_quant_reservation_info_mrp](stock_quant_reservation_info_mrp/) | 15.0.1.0.0 |  | Allows to see the manufacturing order related to the reserved info of Products
[stock_removal_location_by_priority](stock_removal_location_by_priority/) | 15.0.1.0.0 |  | Establish a removal priority on stock locations.
[stock_request](stock_request/) | 15.0.1.8.3 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Internal request for stock
[stock_request_analytic](stock_request_analytic/) | 15.0.1.1.1 | <a href='https://github.com/AaronHForgeFlow'><img src='https://github.com/AaronHForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='AaronHForgeFlow'/></a> | Internal request for stock
[stock_request_bom](stock_request_bom/) | 15.0.1.0.0 |  | Stock Request with BOM Integration
[stock_request_kanban](stock_request_kanban/) | 15.0.1.1.3 | <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Adds a stock request order, and takes stock requests as lines
[stock_request_mrp](stock_request_mrp/) | 15.0.1.3.1 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Manufacturing request for stock
[stock_request_purchase](stock_request_purchase/) | 15.0.1.2.3 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Internal request for stock
[stock_request_separate_picking](stock_request_separate_picking/) | 15.0.1.0.0 |  | Separate one picking per one stock request
[stock_request_submit](stock_request_submit/) | 15.0.1.0.0 |  | Add submit state on Stock Requests
[stock_request_tier_validation](stock_request_tier_validation/) | 15.0.1.0.1 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Extends the functionality of Stock Requests to support a tier validation process.
[stock_reserve](stock_reserve/) | 15.0.1.2.1 |  | Stock reservations on products
[stock_reserve_rule](stock_reserve_rule/) | 15.0.1.1.0 |  | Configure reservation rules by location
[stock_search_supplierinfo_code](stock_search_supplierinfo_code/) | 15.0.1.0.0 |  | Allows to search for picking from supplierinfo code
[stock_secondary_unit](stock_secondary_unit/) | 15.0.2.3.3 |  | Get product quantities in a secondary unit
[stock_valuation_layer_accounting_date](stock_valuation_layer_accounting_date/) | 15.0.1.0.0 |  | Stock Valuation Layer Accounting Date
[stock_warehouse_calendar](stock_warehouse_calendar/) | 15.0.1.0.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> | Adds a calendar to the Warehouse

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
