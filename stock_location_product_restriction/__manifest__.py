# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Product Restriction",
    "summary": """
        Prevent to mix different products into the same stock location""",
    "version": "16.0.1.2.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["lmignon", "rousseldenis"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": ["views/stock_location.xml"],
    "pre_init_hook": "pre_init_hook",
}
