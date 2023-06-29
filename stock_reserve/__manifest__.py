# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Reservation",
    "summary": "Stock reservations on products",
    "version": "16.0.1.1.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "complexity": "normal",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "view/stock_reserve.xml",
        "view/product.xml",
        "data/stock_data.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
    ],
    "auto_install": False,
    "installable": True,
}
