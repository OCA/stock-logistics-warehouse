# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Putaway strategy per product',
    'summary': 'Set a product location and put-away strategy per product',
    'version': '8.0.1.0.1',
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
        'wizard/quick_add_location.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/product_putaway.xml',
    ]
}
