# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Reception Dedicate Picking Type",
    "summary": """Split Stock In and Quality Check
    Receptions Picking Types""",
    "version": "14.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "data/data.xml",
        "views/stock_warehouse.xml",
    ],
}
