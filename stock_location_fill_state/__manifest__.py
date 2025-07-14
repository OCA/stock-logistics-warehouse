# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Fill State",
    "summary": """This module allows to identify the fill state of stock locations""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["base_partition", "stock", "stock_location_pending_move"],
    "maintainers": ["rousseldenis", "jbaudoux"],
    "data": [
        "views/stock_location.xml",
    ],
}
