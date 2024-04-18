# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
{
    "name": "Stock Warehouse Calendar (reordering rules)",
    "summary": "Adds a calendar to the Warehouse for reordering rules",
    "version": "14.0.1.1.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": ["stock_warehouse_calendar"],
    "data": [
        "views/res_config_settings.xml",
        "views/stock_warehouse.xml",
        "views/stock_warehouse_orderpoint.xml",
    ],
    "installable": True,
    "development_status": "Production/Stable",
    "maintainers": ["sebalix"],
}
