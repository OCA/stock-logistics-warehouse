# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Type Group",
    "summary": """This module allows to group operation types under a same object.""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "security/stock_picking_type_group.xml",
        "views/stock_picking_type_group.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": [
        "demo/stock_picking_type_group.xml",
    ],
}
