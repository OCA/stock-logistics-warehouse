# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Putaway Rule",
    "summary": "Manage putaway with rules as in odoo v13.0",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_strategy.xml",
        "views/product.xml",
        "views/stock_location.xml",
    ],
}
