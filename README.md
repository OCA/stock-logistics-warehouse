
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-warehouse&target_branch=19.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml/badge.svg?branch=19.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/pre-commit.yml?query=branch%3A19.0)
[![Build Status](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml/badge.svg?branch=19.0)](https://github.com/OCA/stock-logistics-warehouse/actions/workflows/test.yml?query=branch%3A19.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-warehouse/branch/19.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-warehouse)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-warehouse-19-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-warehouse-19-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Stock Warehouse

Extend the stock related models (warehouse, location, picking, move, lot...) but without impact flows and processes. It's mainly adding fields or buttons.

Are you looking for modules related to logistics? Or would like to contribute
to? There are many repositories with specific purposes. Have a look at this
[README](https://github.com/OCA/wms/blob/19.0/README.md).

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[stock_demand_estimate](stock_demand_estimate/) | 19.0.1.0.0 |  | Allows to create demand estimates.
[stock_inventory](stock_inventory/) | 19.0.1.0.0 |  | Allows to do an easier follow up of the Inventory Adjustments
[stock_inventory_discrepancy](stock_inventory_discrepancy/) | 19.0.1.0.0 |  | Adds the capability to show the discrepancy of every line in an inventory and to block the inventory validation when the discrepancy is over a user defined threshold.
[stock_inventory_justification](stock_inventory_justification/) | 19.0.1.1.0 | <a href='https://github.com/rousseldenis'><img src='https://github.com/rousseldenis.png' width='32' height='32' style='border-radius:50%;' alt='rousseldenis'/></a> <a href='https://github.com/ThomasBinsfeld'><img src='https://github.com/ThomasBinsfeld.png' width='32' height='32' style='border-radius:50%;' alt='ThomasBinsfeld'/></a> | This module allows to set justification on inventories
[stock_inventory_lockdown](stock_inventory_lockdown/) | 19.0.1.0.0 |  | Lock down stock locations during inventories.
[stock_inventory_lockdown_product](stock_inventory_lockdown_product/) | 19.0.1.0.0 |  | Lock down stock locations during inventories for inventoried products
[stock_location_is_sublocation](stock_location_is_sublocation/) | 19.0.1.0.0 |  | Add method to check stock location is sublocation
[stock_location_position](stock_location_position/) | 19.0.1.0.0 |  | Add coordinate attributes on stock location.
[stock_move_quantity_product_uom](stock_move_quantity_product_uom/) | 19.0.1.0.0 |  | computes stock.move's quantity in the uom of the product.
[stock_picking_show_linked](stock_picking_show_linked/) | 19.0.1.0.0 |  | This addon allows to easily access related pickings (in the case of chained routes) through a button in the parent picking view.
[stock_picking_type_user_restriction](stock_picking_type_user_restriction/) | 19.0.1.0.0 | <a href='https://github.com/eLBati'><img src='https://github.com/eLBati.png' width='32' height='32' style='border-radius:50%;' alt='eLBati'/></a> | Restrict some users to see and use only certain picking types
[stock_picking_volume](stock_picking_volume/) | 19.0.1.0.0 | <a href='https://github.com/lmignon'><img src='https://github.com/lmignon.png' width='32' height='32' style='border-radius:50%;' alt='lmignon'/></a> | Compute volume information on stock moves and pickings
[stock_putaway_product_template](stock_putaway_product_template/) | 19.0.1.0.0 | <a href='https://github.com/kevinkhao'><img src='https://github.com/kevinkhao.png' width='32' height='32' style='border-radius:50%;' alt='kevinkhao'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | Add product template in putaway strategies from the product view
[stock_secondary_unit](stock_secondary_unit/) | 19.0.1.0.0 |  | Get product quantities in a secondary unit
[stock_warehouse_calendar](stock_warehouse_calendar/) | 19.0.1.0.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> | Adds a calendar to the Warehouse

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
