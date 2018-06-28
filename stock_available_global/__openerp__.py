# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock available global (All companies)',
    'version': '9.0.1.0.0',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/product_template_view.xml',
        'views/product_product_view.xml',
    ],
    'installable': True,
}
