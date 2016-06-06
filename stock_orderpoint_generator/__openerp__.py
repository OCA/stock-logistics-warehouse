# -*- coding: utf-8 -*-
# © 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Order point generator',
    'summary': 'Mass configuration of stock order points',
    'version': '9.0.1.0.0',
    'author': "Camptocamp, Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'website': "http://www.camptocamp.com",
    'depends': ['stock'],
    'data': [
        "wizard/orderpoint_generator_view.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'auto_install': False,
}
