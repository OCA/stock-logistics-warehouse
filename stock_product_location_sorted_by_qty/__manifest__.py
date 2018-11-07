# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Product Location Sorted by Quantity',
    'summary': 'In the update wizard of quantities for a product, '
               'sort the stock location by quantity',
    'version': '10.0.1.0.0',
    'development_status': 'Production/Stable',
    'category': 'Warehouse Management',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'maintainers': ['chafique-delli'],
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'stock',
    ],
    'data': ['views/stock_change_product_qty_view.xml'],
}
