# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Location Restrict Procurement Group',
    'summary': """
        Allows to restrict location to a dedicated procurement group
        (e.g. : For orders waiting delivery)""",
    'version': '10.0.1.1.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': ['stock'
                ],
    'data': [
        'views/stock_move.xml',
        'views/stock_location.xml',
    ],
    'external_dependencies': {
        'python': ['openupgradelib'],
    },
    'pre_init_hook': 'pre_init_hook',
}
