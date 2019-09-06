# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Putaway Product From",
    "summary": "Manage putaway from product form",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "stock_putaway_abc",
        "stock_putaway_product_form",
    ],
    "data": [
        "views/product.xml",
        "views/product_category.xml",
    ],
}
