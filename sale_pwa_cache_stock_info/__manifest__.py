# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sale PWA Cache Stock Info",
    "summary": "Adds support to cache stock info on sales",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/web",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Tardo"],
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        'sale_pwa_cache',
        'web_widget_one2many_product_picker_sale_stock',
    ],
    "data": [
        'views/sale_order_line_views.xml',
        'data/data.xml',
    ],
}
