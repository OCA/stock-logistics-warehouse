# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Reserve Sales",
    "version": "13.0.1.1.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "complexity": "normal",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["sale_stock", "stock_reserve"],
    "data": [
        "wizard/sale_stock_reserve_view.xml",
        "view/sale.xml",
        "view/stock_reserve.xml",
    ],
    "installable": True,
    "auto_install": False,
}
