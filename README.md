
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-warehouse&target_branch=16.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-warehouse/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-warehouse)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-warehouse-16-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-warehouse-16-0/?utm_source=widget)

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
[account_move_line_product](account_move_line_product/) | 16.0.1.0.0 |  | Displays the product in the journal entries and items
[account_move_line_stock_info](account_move_line_stock_info/) | 16.0.1.1.1 |  | Account Move Line Stock Info
[base_product_merge](base_product_merge/) | 16.0.1.0.1 | [![JasminSForgeFlow](https://github.com/JasminSForgeFlow.png?size=30px)](https://github.com/JasminSForgeFlow) | Merge duplicate products
[procurement_auto_create_group](procurement_auto_create_group/) | 16.0.1.1.0 |  | Allows to configure the system to propose automatically new procurement groups during the procurement run.
[product_packaging_usability](product_packaging_usability/) | 16.0.1.0.1 |  | Add sugar to Product Packaging
[scrap_reason_code](scrap_reason_code/) | 16.0.1.1.0 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Reason code for scrapping
[stock_cycle_count](stock_cycle_count/) | 16.0.1.1.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Adds the capability to schedule cycle counts in a warehouse through different rules defined by the user.
[stock_demand_estimate](stock_demand_estimate/) | 16.0.1.2.0 |  | Allows to create demand estimates.
[stock_demand_estimate_matrix](stock_demand_estimate_matrix/) | 16.0.1.0.0 |  | Allows to create demand estimates.
[stock_exception](stock_exception/) | 16.0.1.1.0 |  | Custom exceptions on stock picking
[stock_helper](stock_helper/) | 16.0.1.1.0 |  | Add methods shared between various stock modules
[stock_inventory](stock_inventory/) | 16.0.2.5.0 |  | Allows to do an easier follow up of the Inventory Adjustments
[stock_inventory_count_to_zero](stock_inventory_count_to_zero/) | 16.0.1.0.0 |  | Request an inventory count filling the quantities to zero as default
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 16.0.1.1.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_justification](stock_inventory_justification/) | 16.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) [![ThomasBinsfeld](https://github.com/ThomasBinsfeld.png?size=30px)](https://github.com/ThomasBinsfeld) | This module allows to set justification on inventories
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 16.0.1.1.0 |  | More filters for inventory adjustments
[stock_location_lockdown](stock_location_lockdown/) | 16.0.1.0.1 |  | Prevent to add stock on locked locations
[stock_location_package_restriction](stock_location_package_restriction/) | 16.0.1.0.0 |  | Control if the location can contain products in a package
[stock_location_position](stock_location_position/) | 16.0.1.0.0 |  | Add coordinate attributes on stock location.
[stock_location_product_restriction](stock_location_product_restriction/) | 16.0.1.1.0 | [![lmignon](https://github.com/lmignon.png?size=30px)](https://github.com/lmignon) [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Prevent to mix different products into the same stock location
[stock_location_zone](stock_location_zone/) | 16.0.1.0.1 |  | Classify locations with zones.
[stock_move_auto_assign](stock_move_auto_assign/) | 16.0.1.1.1 |  | Try to reserve moves when goods enter in a location
[stock_move_auto_assign_auto_release](stock_move_auto_assign_auto_release/) | 16.0.1.1.2 |  | Auto release moves after auto assign
[stock_move_common_dest](stock_move_common_dest/) | 16.0.1.0.1 |  | Adds field for common destination moves
[stock_move_location](stock_move_location/) | 16.0.1.4.0 |  | This module allows to move all stock in a stock location to an other one.
[stock_move_packaging_qty](stock_move_packaging_qty/) | 16.0.1.5.0 | [![yajo](https://github.com/yajo.png?size=30px)](https://github.com/yajo) [![EmilioPascual](https://github.com/EmilioPascual.png?size=30px)](https://github.com/EmilioPascual) | Add packaging fields in the stock moves
[stock_mts_mto_rule](stock_mts_mto_rule/) | 16.0.1.0.1 |  | Add a MTS+MTO route
[stock_package_type_volume](stock_package_type_volume/) | 16.0.1.0.0 |  | Compute volume of a package type
[stock_packaging_calculator](stock_packaging_calculator/) | 16.0.1.0.1 |  | Compute product quantity to pick by packaging
[stock_packaging_calculator_packaging_level](stock_packaging_calculator_packaging_level/) | 16.0.1.0.0 |  | Glue module for packaging level
[stock_picking_batch_packaging_qty](stock_picking_batch_packaging_qty/) | 16.0.1.0.1 | [![EmilioPascual](https://github.com/EmilioPascual.png?size=30px)](https://github.com/EmilioPascual) [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) | Add packaging fields in stock picking batch
[stock_picking_commercial_partner](stock_picking_commercial_partner/) | 16.0.1.0.0 |  | Add Commercial Partner on the Stock Picking
[stock_picking_procure_method](stock_picking_procure_method/) | 16.0.1.0.0 |  | Allows to force the procurement method from the picking
[stock_picking_product_interchangeable](stock_picking_product_interchangeable/) | 16.0.1.0.0 | [![CetmixGitDrone](https://github.com/CetmixGitDrone.png?size=30px)](https://github.com/CetmixGitDrone) | Stock Picking Product Interchangeable
[stock_picking_show_linked](stock_picking_show_linked/) | 16.0.1.0.0 |  | This addon allows to easily access related pickings (in the case of chained routes) through a button in the parent picking view.
[stock_picking_volume](stock_picking_volume/) | 16.0.1.0.4 | [![lmignon](https://github.com/lmignon.png?size=30px)](https://github.com/lmignon) | Compute volume information on stock moves and pickings
[stock_picking_volume_packaging](stock_picking_volume_packaging/) | 16.0.1.0.1 |  | Use volume information on potential product packaging to compute the volume of a stock.move
[stock_product_qty_by_packaging](stock_product_qty_by_packaging/) | 16.0.1.0.0 |  | Compute product quantity to pick by packaging
[stock_production_lot_quantity_tree](stock_production_lot_quantity_tree/) | 16.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Allows to display product quantity field on production lot tree view
[stock_pull_list](stock_pull_list/) | 16.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | The pull list checks the stock situation and calculates needed quantities.
[stock_putaway_product_template](stock_putaway_product_template/) | 16.0.1.1.0 | [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Add product template in putaway strategies from the product view
[stock_quant_cost_info](stock_quant_cost_info/) | 16.0.1.0.0 |  | Shows the cost of the quants
[stock_quant_expiration_date_tree](stock_quant_expiration_date_tree/) | 16.0.1.0.0 | [![Manuel Calero](https://github.com/Manuel Calero.png?size=30px)](https://github.com/Manuel Calero) | Allows to display expirations dates on stock quant tree view
[stock_quant_manual_assign](stock_quant_manual_assign/) | 16.0.1.1.1 |  | Stock - Manual Quant Assignment
[stock_quant_reservation_info](stock_quant_reservation_info/) | 16.0.1.0.1 |  | Allows to see the reserved info of Products
[stock_quant_reservation_info_mrp](stock_quant_reservation_info_mrp/) | 16.0.1.0.0 |  | Allows to see the manufacturing order related to the reserved info of Products
[stock_quant_safe_inventory](stock_quant_safe_inventory/) | 16.0.1.0.0 |  | Prevents the quantity on the quant from being updated if quantities have already been picked but not validated in pickings in progress.
[stock_removal_location_by_priority](stock_removal_location_by_priority/) | 16.0.1.0.0 |  | Establish a removal priority on stock locations.
[stock_reservation_date_show](stock_reservation_date_show/) | 16.0.1.0.0 |  | Display reservation date of stock moves
[stock_reserve](stock_reserve/) | 16.0.1.3.1 |  | Stock reservations on products
[stock_reserve_rule](stock_reserve_rule/) | 16.0.1.0.0 |  | Configure reservation rules by location
[stock_route_mto](stock_route_mto/) | 16.0.1.0.0 |  | Allows to identify MTO routes through a checkbox and availability to filter them.
[stock_scrap_location_default](stock_scrap_location_default/) | 16.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Allows to define a setting at company level that reference a default scrap location
[stock_search_supplierinfo_code](stock_search_supplierinfo_code/) | 16.0.1.0.1 |  | Allows to search for picking from supplierinfo code
[stock_secondary_unit](stock_secondary_unit/) | 16.0.1.1.0 |  | Get product quantities in a secondary unit
[stock_storage_category_capacity_name](stock_storage_category_capacity_name/) | 16.0.1.0.0 |  | Allows to have a better display name for Stock Storage Category Capacity model
[stock_valuation_layer_accounting_date](stock_valuation_layer_accounting_date/) | 16.0.1.0.0 |  | Stock Valuation Layer Accounting Date
[stock_valuation_layer_inventory_filter](stock_valuation_layer_inventory_filter/) | 16.0.1.0.1 | [![Shide](https://github.com/Shide.png?size=30px)](https://github.com/Shide) | Allows to filter Inventory Adjustments on Stock Valuation Layers
[stock_valuation_layer_total_value](stock_valuation_layer_total_value/) | 16.0.1.0.0 |  | Show total value on tree and form view
[stock_vlm_mgmt](stock_vlm_mgmt/) | 16.0.1.0.2 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Light self contained alternative for VLM integrations
[stock_warehouse_calendar](stock_warehouse_calendar/) | 16.0.1.0.0 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) | Adds a calendar to the Warehouse
[stock_warehouse_relationship](stock_warehouse_relationship/) | 16.0.1.0.0 | [![petrus-v](https://github.com/petrus-v.png?size=30px)](https://github.com/petrus-v) | Technical module to add warehouse_id field on various stock.* models


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[stock_package_type_button_box](stock_package_type_button_box/) | 16.0.1.0.0 (unported) | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | DEPRECATED - This module is a technical module that allows to fill in a button box for Stock Package Type form view

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
