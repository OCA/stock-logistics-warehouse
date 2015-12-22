# -*- coding: utf-8 -*-
# © 2015 ClearCorp S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Reserve MRP',
    'version': '8.0.1.0.0',
    'category': 'Manufacturing',
    'sequence': 10,
    'summary': 'Automatic reservation of consumed products'
    'in production orders',
    'author': 'ClearCorp,Odoo Community Association (OCA)',
    'website': 'http://clearcorp.co.cr',
    'depends': ['mrp', 'stock_reserve'],
    'data': ['stock_reserve_mrp_view.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
