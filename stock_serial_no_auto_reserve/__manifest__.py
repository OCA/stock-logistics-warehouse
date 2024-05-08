# Copyright 2024 Sunflower IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Serial No Auto-Reserve",
    "summary": "Optionally prevent ...",
    "version": "14.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Sunflower IT, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "data": [
        "views/product_templates.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
