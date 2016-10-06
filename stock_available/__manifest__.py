# -*- coding: utf-8 -*-
# © 2014 Numérigraphe, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock available to promise',
    'version': '9.0.1.1.0',
    "author": "Numérigraphe, Sodexis, Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'depends': ['stock'],
    'license': 'AGPL-3',
    'data': [
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
}
