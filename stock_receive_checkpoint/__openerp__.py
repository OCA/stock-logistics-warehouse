# -*- coding: utf-8 -*-
# Copyright (C) 2021 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Reception Checkpoint",
    "version": "8.0.1.0.0",
    "category": "Stock",
    "website": "https://akretion.com",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        "purchase",
        "stock",
    ],
    "data": [
        "views/stock_view.xml",
        "wizards/checkpoint_view.xml",
    ],
}
