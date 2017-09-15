# -*- coding: utf-8 -*-
# © 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Reorder Limit",
    "summary": "Sensible limits on minimum stock rule processing",
    "author":
        "Therp BV, "
        "Odoo Community Association (OCA)",
    "website": "https://therp.nl",
    "category": "Warehouse",
    "license": "AGPL-3",
    "version": "8.0.1.0.0",
    "depends": [
        "purchase",
        "stock_warehouse_orderpoint_stock_info",
    ],
    "data": [
        "views/stock_warehouse_orderpoint.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
