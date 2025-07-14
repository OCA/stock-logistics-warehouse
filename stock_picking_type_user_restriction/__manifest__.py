# Copyright 2020 Lorenzo Battistini @ TAKOBI
# Copyright 2021 Daniel Domínguez López (https://xtendoo.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock picking type - Restrict users",
    "summary": "Restrict some users to see and use only certain picking types",
    "version": "14.0.1.0.2",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Xtendoo, TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/stock_security.xml",
        "views/stock_picking_type_views.xml",
        "security/ir.model.access.csv",
        "views/stock_menu_views.xml",
        "views/product_views.xml",
        "views/stock_inventory_views.xml",
        "views/stock_picking_views.xml",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
}
