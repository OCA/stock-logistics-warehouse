# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Move Product Default Packaging Level",
    "summary": """This module allows to show on stock move levels
    the default packaging from default packaging level""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock", "product_packaging_level"],
    "data": [
        "views/stock_picking.xml",
        "views/stock_move_line.xml",
        "views/stock_move.xml",
    ],
}
