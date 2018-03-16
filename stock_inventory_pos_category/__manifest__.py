# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Inventory POS Category',
    'version': '10.0.1.0.0',
    'category': 'Inventory, Logistics, Warehousing',
    'license': 'AGPL-3',
    'summary': 'Create an inventory for one or several POS categories',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['stock', 'point_of_sale'],
    'data': [
        'views/stock_inventory.xml',
    ],
    'installable': True,
}
