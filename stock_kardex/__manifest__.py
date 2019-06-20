# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Kardex',
    'summary': 'Provides interaction and GUI for Kardex',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'barcodes',
        'base_sparse_field',
    ],
    'website': 'https://www.camptocamp.com',
    'data': [
        'views/stock_location_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_picking_type_views.xml',
        'views/stock_kardex_views.xml',
        'views/stock_kardex_tray_type_views.xml',
        'views/stock_kardex_templates.xml',
        'data/stock_location.xml',
        'data/stock_kardex_tray_type.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
