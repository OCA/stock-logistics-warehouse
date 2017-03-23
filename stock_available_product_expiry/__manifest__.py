# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Expiry Available',
    'summary': """
        Allows to get product availability taking into account lot removal date
        """,
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': ['stock',
                'product_expiry'
                ],
    'data': ['views/res_config.xml',
             ],
    'demo': [
    ],
    'installable': True,
}
