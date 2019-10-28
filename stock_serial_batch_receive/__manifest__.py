# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Serial Number Batch",
    "summary": "Generate serial number automatically per batch",
    "version": "12.0.1.0.0",
    "category": "Stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainer": "Camptocamp",
    "website": "http://www.github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_move.xml",
        "wizard/stock_move_line_serial_generator.xml",
    ],
}
