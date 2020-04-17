# Copyright 2020 Camptocamp SA.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Stock Reserve Sales',
    'version': '1.0',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'complexity': 'normal',
    'images': [],
    'website': "http://www.camptocamp.com",
    'depends': [
        'sale_stock',
        'stock_reserve',
    ],
    'demo': [],
    'data': [
        'wizard/sale_stock_reserve_view.xml',
        'view/sale.xml',
        'view/stock_reserve.xml',
    ],
    'installable': True,
    'auto_install': False,
}
