# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Procurement Calendar Purchase',
    'summary': """
        Allow to define procurement calendars to manage fixed procure dates
         (base for purchase, mrp, ...)
    """,
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'purchase',
        'stock_procurement_calendar',
        'stock_orderpoint_manual_procurement',
    ],
    'data': [
        'views/stock_warehouse_orderpoint.xml'
    ],
    'demo': [
        'demo/procurement_calendar.xml'
    ]
}
