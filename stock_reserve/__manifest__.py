# Copyright 2020 Camptocamp SA.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Stock Reservation',
    'summary': 'Stock reservations on products',
    'version': '11.0.1.0.0',
    'author': "Camptocamp, Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'complexity': 'normal',
    'images': [],
    'website': "http://www.camptocamp.com",
    'depends': [
        'stock',
    ],
    'demo': [],
    'data': [
        'view/stock_reserve.xml',
        'view/product.xml',
        'data/stock_data.xml',
        'security/ir.model.access.csv',
    ],
    'auto_install': False,
    'test': [
        'test/stock_reserve.yml',
    ],
    'installable': True,
}
