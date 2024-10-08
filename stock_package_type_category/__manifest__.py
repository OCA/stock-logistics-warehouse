# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Package Type Category",
    "summary": """
        This module allows to group package types in different categories""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "security/stock_package_type_category.xml",
        "views/stock_package_type_category.xml",
        "views/stock_package_type.xml",
    ],
    "demo": [
        "demo/stock_package_type_category.xml",
    ],
}
