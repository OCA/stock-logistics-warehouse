# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Package Type Button Box",
    "summary": """
        DEPRECATED - This module is a technical module that allows to fill in a button box
        for Stock Package Type form view""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "installable": False,
    "data": [
        "views/stock_package_type.xml",
    ],
}
