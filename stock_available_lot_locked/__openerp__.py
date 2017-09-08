# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Consider the blocked lots are not available to promise',
    'version': '8.0.1.0.0',
    "author": u"Numérigraphe,"
              u"Odoo Community Association (OCA)",
    'category': 'Hidden',
    'depends': [
        'stock_available',
        'stock_lock_lot'
    ],
    'data': [
        'views/product_template_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
