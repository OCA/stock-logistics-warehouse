# -*- coding: utf-8 -*-
# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Warehouse Multi Security",
    "version": "12.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "summary": "Restrict access in multi warehouse environment",
    "depends": [
        "base_multi_warehouse",
    ],
    "data": [
        'security/stock_security.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
        'views/stock_inventory.xml',
        'views/stock_location.xml',
        'views/stock_quant_package.xml',
        'views/stock_quant.xml',
        'views/res_users.xml',
        'views/stock_move_line.xml',
    ],
}
