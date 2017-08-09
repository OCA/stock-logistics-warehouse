# -*- coding: utf-8 -*-
# Copyright 2015 Mikel Arregi - AvanzOSC
# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2017 Eficent - Jordi Ballester
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock - Manual Quant Assignment",
    "version": "10.0.1.0.0",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "author": "AvanzOSC, "
              "Tecnativa, "
              "Eficent, "
              "Fanha Giang, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org",
    "depends": [
        "stock",
    ],
    "data": [
        "wizard/assign_manual_quants_view.xml",
        "views/stock_move_view.xml",
    ],
    "installable": True,
}
