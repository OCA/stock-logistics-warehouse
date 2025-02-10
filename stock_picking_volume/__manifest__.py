# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Volume",
    "summary": """
        Compute volume information on stock moves and pickings""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "maintainers": ["lmignon"],
    "depends": [
        "product_dimension",
        "stock",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_move.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    "development_status": "Beta",
}
