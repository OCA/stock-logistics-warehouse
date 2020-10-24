# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Product Restriction",
    "summary": """
        Prevent to mix different products into the same stock location""",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://acsone.eu/",
    "depends": ["stock"],
    "data": ["views/stock_location.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}
