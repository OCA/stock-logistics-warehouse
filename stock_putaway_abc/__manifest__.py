# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Putaway ABC",
    "summary": "Manage ABC Chaotic storage putaway",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_putaway_rule"
    ],
    "data": [
        "views/stock_location.xml",
        "views/product_strategy.xml",
    ],
    "demo": [
        "demo/stock_location.xml",
        "demo/product_strategy.xml",
    ],
}
