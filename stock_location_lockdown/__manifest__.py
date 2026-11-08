# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Lockdown",
    "summary": "Prevent to add stock on locked locations",
    "author": "Akretion, Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "version": "18.0.1.1.0",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "depends": ["stock", "stock_inventory"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/stock_location.xml",
    ],
}
