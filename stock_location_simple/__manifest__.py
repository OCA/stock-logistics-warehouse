# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Simple",
    "summary": "Simplified stock.location menu",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": ["views/stock_location_views.xml"],
    "post_init_hook": "post_init_hook",
}
