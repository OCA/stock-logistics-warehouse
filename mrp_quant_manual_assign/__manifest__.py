# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mrp Quant Manual Assign",
    "summary": """
        MRP layer of stock_quant_manual_assign module""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["mrp", "stock_quant_manual_assign"],
    "data": [
        "views/stock_move_view.xml",
    ],
}
