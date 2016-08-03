# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Products Default Location',
    'version': '7.0.1.0.0',
    "author": "initos GmbH, Odoo Community Association (OCA)",
    "website": "http://www.initos.com",
    "license": "AGPL-3",
    "category": "",
    "description": """
This module allows to set a default location for the product
and fill this location automatically in stock move according to
the picking type.
    """,
    'depends': [
        'product',
        'stock',
    ],
    "data": [
        'product_view.xml',
        'stock_move_view.xml',
    ],
    'installable': True,
    'active': False,
}
