# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Packaging',
    'summary': """
        Allows to propagate packaging through stock flows""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': ['rousseldenis'],
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'depends': [
        'stock',
        'packaging_uom',
    ],
    'data': [
        'views/stock_rule.xml',
    ],
}
