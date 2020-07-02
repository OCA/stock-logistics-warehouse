# Copyright 2020 Lorenzo Battistini @ TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock picking type - Restrict users",
    "summary": "Restrict some users to see and use only certain picking types",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "security/stock_security.xml",
        "views/stock_picking_type_views.xml",
        "security/ir.model.access.csv",
        "views/stock_menu_views.xml",
        "views/product_views.xml",
        "views/stock_inventory_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_warehouse_views.xml",
    ],
}
