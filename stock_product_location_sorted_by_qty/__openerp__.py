# -*- coding: utf-8 -*-
# © 2017 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Product Location Sorted by Quantity',
    'summary': 'In the update wizard of quantities for a product, '
               'sort the stock location by quantity',
    'version': '8.0.1.0.0',
    'category': 'Warehouse Management',
    'website': 'http://akretion.com',
    'author': 'Akretion',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'stock',
    ],
    'data': ['views/stock_change_product_qty_view.xml'],
}
