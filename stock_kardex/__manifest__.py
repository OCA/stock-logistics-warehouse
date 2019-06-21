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
    'demo': [
        'demo/stock_location_demo.xml',
        'demo/stock_kardex_demo.xml',
        'demo/product_demo.xml',
        'demo/stock_inventory_demo.xml',
        'demo/stock_picking_demo.xml',
    ],
    'data': [
        'views/stock_location_views.xml',
        'views/stock_kardex_views.xml',
        'views/stock_kardex_tray_type_views.xml',
        'views/stock_kardex_templates.xml',
        'templates/kardex_screen.xml',
        'data/stock_location.xml',
        'data/stock_kardex_tray_type.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
