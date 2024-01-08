# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Inventory Justification",
    "summary": """
        This module allows to set justification on inventories""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "maintainers": ["rousseldenis", "ThomasBinsfeld"],
    "depends": ["stock"],
    "data": [
        "security/acl_stock_inventory_justification.xml",
        "views/stock_move_line.xml",
        "views/stock_quant.xml",
        "views/stock_inventory_justification.xml",
    ],
}
