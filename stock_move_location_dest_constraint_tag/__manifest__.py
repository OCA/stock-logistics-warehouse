# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Move Location Dest Constraints Tag",
    "summary": "Constrain location dest according to product tags",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_move_location_dest_constraint_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_storage_tag.xml",
        "views/product_template.xml",
        "views/stock_location.xml",
    ],
    "demo": [
        "demo/product_storage_tag.xml",
        "demo/product_category.xml",
        "demo/product.xml",
        "demo/stock_location.xml",
        "demo/product_putaway.xml",
    ],
}
