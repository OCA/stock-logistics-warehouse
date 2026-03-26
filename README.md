
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-warehouse&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-warehouse/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-warehouse)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-warehouse-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-warehouse-17-0/?utm_source=widget)

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
[account_move_line_product](account_move_line_product/) | 17.0.1.0.0 |  | Displays the product in the journal entries and items
[account_move_line_stock_info](account_move_line_stock_info/) | 17.0.1.0.0 |  | Account Move Line Stock Info
[base_product_merge](base_product_merge/) | 17.0.1.0.0 | <a href='https://github.com/JasminSForgeFlow'><img src='https://github.com/JasminSForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JasminSForgeFlow'/></a> | Merge duplicate products
[procurement_auto_create_group](procurement_auto_create_group/) | 17.0.1.0.0 |  | Allows to configure the system to propose automatically new procurement groups during the procurement run.
[product_route_profile](product_route_profile/) | 17.0.1.0.0 | <a href='https://github.com/Kev-Roche'><img src='https://github.com/Kev-Roche.png' width='32' height='32' style='border-radius:50%;' alt='Kev-Roche'/></a> | Add Route profile concept on product
[scrap_reason_code](scrap_reason_code/) | 17.0.1.0.1 | <a href='https://github.com/bodedra'><img src='https://github.com/bodedra.png' width='32' height='32' style='border-radius:50%;' alt='bodedra'/></a> | Reason code for scrapping
[stock_account_change_qty_reason](stock_account_change_qty_reason/) | 17.0.1.0.0 |  | Stock Account Change Quantity Reason
[stock_archive_constraint](stock_archive_constraint/) | 17.0.1.0.0 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Stock archive constraint
[stock_change_qty_reason](stock_change_qty_reason/) | 17.0.1.0.0 |  | Stock Quantity Change Reason
[stock_demand_estimate](stock_demand_estimate/) | 17.0.1.1.1 |  | Allows to create demand estimates.
[stock_demand_estimate_matrix](stock_demand_estimate_matrix/) | 17.0.1.0.0 |  | Allows to create demand estimates.
[stock_exception](stock_exception/) | 17.0.1.0.0 |  | Custom exceptions on stock picking
[stock_helper](stock_helper/) | 17.0.1.1.1 |  | Add methods shared between various stock modules
[stock_inventory](stock_inventory/) | 17.0.1.3.0 |  | Allows to do an easier follow up of the Inventory Adjustments
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 17.0.1.1.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 17.0.1.0.0 |  | More filters for inventory adjustments
[stock_location_lockdown](stock_location_lockdown/) | 17.0.1.0.0 |  | Prevent to add stock on locked locations
[stock_location_position](stock_location_position/) | 17.0.1.0.0 |  | Add coordinate attributes on stock location.
[stock_location_zone](stock_location_zone/) | 17.0.1.0.0 |  | Classify locations with zones.
[stock_move_location](stock_move_location/) | 17.0.1.0.0 |  | This module allows to move all stock in a stock location to an other one.
[stock_mts_mto_rule](stock_mts_mto_rule/) | 17.0.1.0.1 |  | Add a MTS+MTO route
[stock_packaging_calculator](stock_packaging_calculator/) | 17.0.1.1.0 |  | Compute product quantity to pick by packaging
[stock_picking_show_linked](stock_picking_show_linked/) | 17.0.1.0.0 |  | This addon allows to easily access related pickings (in the case of chained routes) through a button in the parent picking view.
[stock_picking_volume](stock_picking_volume/) | 17.0.1.1.0 | <a href='https://github.com/lmignon'><img src='https://github.com/lmignon.png' width='32' height='32' style='border-radius:50%;' alt='lmignon'/></a> | Compute volume information on stock moves and pickings
[stock_picking_volume_packaging](stock_picking_volume_packaging/) | 17.0.1.0.0 |  | Use volume information on potential product packaging to compute the volume of a stock.move
[stock_putaway_product_template](stock_putaway_product_template/) | 17.0.1.0.0 | <a href='https://github.com/kevinkhao'><img src='https://github.com/kevinkhao.png' width='32' height='32' style='border-radius:50%;' alt='kevinkhao'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | Add product template in putaway strategies from the product view
[stock_quant_manual_assign](stock_quant_manual_assign/) | 17.0.1.1.0 |  | Stock - Manual Quant Assignment
[stock_quant_reservation_info](stock_quant_reservation_info/) | 17.0.1.0.1 |  | Allows to see the reserved info of Products
[stock_quant_reservation_info_mrp](stock_quant_reservation_info_mrp/) | 17.0.1.0.0 |  | Allows to see the manufacturing order related to the reserved info of Products
[stock_removal_location_by_priority](stock_removal_location_by_priority/) | 17.0.1.0.0 |  | Establish a removal priority on stock locations.
[stock_reserve](stock_reserve/) | 17.0.1.0.0 |  | Stock reservations on products
[stock_reserve_sale](stock_reserve_sale/) | 17.0.1.0.0 |  | Stock Reserve Sales
[stock_route_mto](stock_route_mto/) | 17.0.1.0.0 |  | Allows to identify MTO routes through a checkbox and availability to filter them.
[stock_search_supplierinfo_code](stock_search_supplierinfo_code/) | 17.0.1.0.0 |  | Allows to search for picking from supplierinfo code
[stock_secondary_unit](stock_secondary_unit/) | 17.0.1.1.0 |  | Get product quantities in a secondary unit
[stock_warehouse_calendar](stock_warehouse_calendar/) | 17.0.1.0.1 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> | Adds a calendar to the Warehouse

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
