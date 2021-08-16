# -*- coding: utf-8 -*-
# © 2016 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Automatic Workflow: Reserve Sale stock',
    'version': '8.0.0.1.0',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'author': "FactorLibre,Odoo Community Association (OCA)",
    'website': 'http://www.factorlibre.com/',
    'depends': [
        'sale_automatic_workflow',
        'stock_reserve_sale'
    ],
    'data': [
        'views/sale_workflow_process_view.xml'
    ],
    'installable': True,
}
