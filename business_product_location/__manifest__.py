# -*- coding: utf-8 -*-
# Copyright 2015-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Business Product Location',
    'version': '10.0.1.0.0',
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'category': 'Warehouse Management',
    'website': 'http://www.acsone.eu',
    'depends': [
        'stock',
    ],
    'data': [
        'views/business_product_location_views.xml',
        'views/business_product_location_templates.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
