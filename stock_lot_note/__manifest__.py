# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Lot Note',
    'summary': """
        Adds a field to fill in notes in lots""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'maintainers': ['rousseldenis'],
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_production_lot.xml',
    ],
}
