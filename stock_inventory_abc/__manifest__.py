# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Inventory ABC",
    "summary": "This module allows you to implement ABC Analysis \
and configure cycle count rules using the ABC group.",
    "version": "14.0.1.0.0",
    "maintainers": ["opensourceintegrators"],
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock_cycle_count"],
    "data": [
        "data/stock_abc_data.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/product_template_view.xml",
        "views/stock_abc_views.xml",
        "views/stock_count_rule_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
