# -*- coding: utf-8 -*-
{
    'name': 'Putaway strategy per product',
    'summary': 'Set a product location per product',
    'version': '8.0.0.1',
    'category': 'Inventory',
    'website': 'http://www.apertoso.be',
    'author': 'Apertoso N.V., Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'applicaton': False,
    'installable': True,
    'depends': [
        'product',
        'stock'
    ],
    'data': [
        'views/product.xml',
        'views/product_putaway.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/product_putaway.xml',
    ]
}
