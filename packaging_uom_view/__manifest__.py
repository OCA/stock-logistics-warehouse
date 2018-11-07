# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Packaging Uom View',
    'summary': """
        If purchase is installed along with packaging_uom,
        there is a duplicate view""",
    'version': '10.0.1.0.0',
    'development_status': 'Alpha',
    'maintainers': ['rousseldenis'],
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'purchase',
        'packaging_uom',
    ],
    'data': [
        'views/product_template.xml',
    ],
    'auto_install': True,
}
