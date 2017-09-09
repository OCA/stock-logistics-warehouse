# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# (c) 2016 Tecnativa - Pedro M. Baeza
# (c) 2017 Eficent - Jordi Ballester
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock - Manual Quant Assignment",
    "version": "9.0.1.1.0",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "author": "AvanzOSC, "
              "Tecnativa, "
              "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "depends": [
        "stock",
    ],
    "data": [
        "wizard/assign_manual_quants_view.xml",
        "views/stock_move_view.xml",
    ],
    "installable": True,
}
