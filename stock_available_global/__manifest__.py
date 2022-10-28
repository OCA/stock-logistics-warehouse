# Copyright 2016-2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock available global (All companies)',
    'version': '11.0.1.0.1',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/product_template_view.xml',
        'views/product_product_view.xml',
    ],
    'installable': True,
}
