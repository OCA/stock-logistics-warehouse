# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Pending Move",
    "summary": """
        This module allows to show pending stock moves (outgoing and incoming)
        on a stock location""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,BCIM,Camptocamp,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis", "jbaudoux"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": ["views/stock_location.xml"],
}
