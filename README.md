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
[scrap_reason_code](scrap_reason_code/) | 14.0.1.0.0 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Reason code for scrapping
[stock_archive_constraint](stock_archive_constraint/) | 14.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock archive constraint
[stock_available](stock_available/) | 14.0.1.0.2 |  | Stock available to promise
[stock_available_immediately](stock_available_immediately/) | 14.0.1.0.0 |  | Ignore planned receptions in quantity available to promise
[stock_available_mrp](stock_available_mrp/) | 14.0.1.0.2 |  | Consider the production potential is available to promise
[stock_available_unreserved](stock_available_unreserved/) | 14.0.1.0.1 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Quantity of stock available for immediate use
[stock_demand_estimate](stock_demand_estimate/) | 14.0.1.1.0 |  | Allows to create demand estimates.
[stock_demand_estimate_matrix](stock_demand_estimate_matrix/) | 14.0.1.0.0 |  | Allows to create demand estimates.
[stock_free_quantity](stock_free_quantity/) | 14.0.1.0.0 |  | Stock Free Quantity
[stock_generate_putaway_from_inventory](stock_generate_putaway_from_inventory/) | 14.0.1.0.0 | [![pierrickbrun](https://github.com/pierrickbrun.png?size=30px)](https://github.com/pierrickbrun) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) | Generate Putaway locations per Product deduced from Inventory
[stock_helper](stock_helper/) | 14.0.1.0.0 |  | Add methods shared between various stock modules
[stock_inventory_preparation_filter](stock_inventory_preparation_filter/) | 14.0.1.0.0 |  | More filters for inventory adjustments
[stock_location_bin_name](stock_location_bin_name/) | 14.0.1.0.0 |  | Compute bin stock location name automatically
[stock_location_children](stock_location_children/) | 14.0.1.0.0 |  | Add relation between stock location and all its children
[stock_location_lockdown](stock_location_lockdown/) | 14.0.1.0.0 |  | Prevent to add stock on locked locations
[stock_location_position](stock_location_position/) | 14.0.1.0.0 |  | Add coordinate attributes on stock location.
[stock_location_tray](stock_location_tray/) | 14.0.1.1.0 |  | Organize a location as a matrix of cells
[stock_location_zone](stock_location_zone/) | 14.0.1.0.0 |  | Classify locations with zones.
[stock_measuring_device](stock_measuring_device/) | 14.0.1.0.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) | Implement a common interface for measuring and weighing devices
[stock_measuring_device_zippcube](stock_measuring_device_zippcube/) | 14.0.1.0.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) | Implement interface with Bosche Zippcube devicesfor packaging measurement
[stock_move_common_dest](stock_move_common_dest/) | 14.0.1.0.0 |  | Adds field for common destination moves
[stock_move_location](stock_move_location/) | 14.0.1.0.0 |  | This module allows to move all stock in a stock location to an other one.
[stock_orderpoint_move_link](stock_orderpoint_move_link/) | 14.0.1.0.0 |  | Link Reordering rules to stock moves
[stock_orderpoint_purchase_link](stock_orderpoint_purchase_link/) | 14.0.1.0.0 |  | Link Reordering rules to purchase orders
[stock_packaging_calculator](stock_packaging_calculator/) | 14.0.1.1.0 |  | Compute product quantity to pick by packaging
[stock_picking_cancel_confirm](stock_picking_cancel_confirm/) | 14.0.1.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Stock Picking Cancel Confirm
[stock_pull_list](stock_pull_list/) | 14.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | The pull list checks the stock situation and calculates needed quantities.
[stock_putaway_method](stock_putaway_method/) | 14.0.1.0.0 | [![asaunier](https://github.com/asaunier.png?size=30px)](https://github.com/asaunier) | Add the putaway strategy method back, removed from the stock module in Odoo 12
[stock_quant_manual_assign](stock_quant_manual_assign/) | 14.0.1.1.0 |  | Stock - Manual Quant Assignment
[stock_request](stock_request/) | 14.0.1.0.3 |  | Internal request for stock
[stock_request_picking_type](stock_request_picking_type/) | 14.0.1.0.0 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Add Stock Requests to the Inventory App
[stock_reserve_rule](stock_reserve_rule/) | 14.0.1.0.0 |  | Configure reservation rules by location
[stock_search_supplierinfo_code](stock_search_supplierinfo_code/) | 14.0.1.0.0 |  | Allows to search for picking from supplierinfo code
[stock_vertical_lift](stock_vertical_lift/) | 14.0.1.0.0 |  | Provides the core for integration with Vertical Lifts
[stock_vertical_lift_kardex](stock_vertical_lift_kardex/) | 14.0.1.0.0 |  | Integrate with Kardex Remstar Vertical Lifts
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
