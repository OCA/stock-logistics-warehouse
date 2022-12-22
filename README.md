
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
[scrap_reason_code](scrap_reason_code/) | 16.0.1.0.2 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Reason code for scrapping
[stock_demand_estimate](stock_demand_estimate/) | 16.0.1.0.1 |  | Allows to create demand estimates.
[stock_helper](stock_helper/) | 16.0.1.0.1 |  | Add methods shared between various stock modules
[stock_location_product_restriction](stock_location_product_restriction/) | 16.0.1.0.0 | [![lmignon](https://github.com/lmignon.png?size=30px)](https://github.com/lmignon) [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Prevent to mix different products into the same stock location
[stock_location_zone](stock_location_zone/) | 16.0.1.0.1 |  | Classify locations with zones.
[stock_move_auto_assign](stock_move_auto_assign/) | 16.0.1.0.0 |  | Try to reserve moves when goods enter in a location
[stock_move_common_dest](stock_move_common_dest/) | 16.0.1.0.1 |  | Adds field for common destination moves
[stock_move_location](stock_move_location/) | 16.0.1.0.1 |  | This module allows to move all stock in a stock location to an other one.
[stock_mts_mto_rule](stock_mts_mto_rule/) | 16.0.1.0.0 |  | Add a MTS+MTO route
[stock_search_supplierinfo_code](stock_search_supplierinfo_code/) | 16.0.1.0.1 |  | Allows to search for picking from supplierinfo code
[stock_warehouse_calendar](stock_warehouse_calendar/) | 16.0.1.0.0 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) | Adds a calendar to the Warehouse


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
