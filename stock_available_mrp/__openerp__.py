# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL, Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Consider the production potential is available to promise',
    'version': '9.0.1.0.0',
    "author": u"Numérigraphe,"
              u"Odoo Community Association (OCA)",
    'category': 'Hidden',
    'depends': [
        'stock_available',
        'mrp'
    ],
    'data': [
        'views/product_template_view.xml',
    ],
    'demo': [
        'demo/mrp_bom.yml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
