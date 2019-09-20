# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Reminder",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Stock",
    "summary": "Set reminders for products",
    "depends": [
        'stock',
    ],
    "data": [
        'views/stock_reminder.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": False,
}
