# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Production Lot Quantity Tree',
    'summary': """
        Allows to display product quantity field on production lot tree view""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'maintainers': ['rousseldenis'],
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_production_lot.xml',
    ],
}
