# -*- coding: utf-8 -*-
# (c) 2016 credativ ltd. - Ondřej Kuzník
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Owner Lot Visibility',
    'summary': 'Show lots on the partners that own them',
    'version': '9.0.1.0.0',
    'category': 'Generic Modules/Inventory Control',
    'author': 'credativ ltd., '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
}
