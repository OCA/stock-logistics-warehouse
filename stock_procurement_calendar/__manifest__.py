# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Procurement Calendar',
    'summary': """
        Allow to define procurement calendars to manage fixed procure dates
         (base for purchase, mrp, ...)
    """,
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'procurement',
        'web_widget_timepicker',
        'web_timeline',
        'stock',
        'resource',
        'purchase'
    ],
    'exclude': [
        'stock_calendar'
    ],
    'data': [
        'security/procurement_calendar_attendance.xml',
        'security/procurement_calendar.xml',
        'views/procurement_order.xml',
        'views/res_partner.xml',
        'views/product_template.xml',
        'views/procurement_calendar.xml',
        'views/procurement_calendar_attendance.xml',
    ],
    'demo': [
        'demo/procurement_calendar.xml',
    ],
}
