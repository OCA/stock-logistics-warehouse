# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Quotations in quantity available to promise',
    'version': '8.0.3.0.0',
    "author": u"Numérigraphe,Odoo Community Association (OCA)",
    'category': 'Hidden',
    'depends': [
        'stock_available',
        'sale_order_dates',
        'sale_stock',
    ],
    'data': [
        'views/product_template_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
