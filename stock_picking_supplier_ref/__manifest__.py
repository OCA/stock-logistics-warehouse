# -*- coding: utf-8 -*-
# Copyright 2017 Trey, Kilobytes de Soluciones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Picking Supplier Reference',
    'version': '10.0.1.0.0',
    'category': 'Stock',
    'author': 'Trey, Odoo Community Association (OCA)',
    'website': 'https://www.trey.es',
    'license': 'AGPL-3',
    'description': '''
        Adds a supplier reference field inside supplier's pickings and
        allows search for this reference.''',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_picking.xml',
    ],
    'installable': True,
}
