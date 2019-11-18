# Copyright 2019  Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock picking location info',
    'version': '12.0.1.0.0',
    'author': "Eficent, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/stock-logistics-warehouse",
    'category': 'Stock',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'development_status': 'Alpha',
    'license': 'AGPL-3',
}
