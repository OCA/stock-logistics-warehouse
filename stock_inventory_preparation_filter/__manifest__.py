# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOSC - Oihane Crucelaegi
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Extended Inventory Preparation Filters",
    "version": "10.0.1.0.0",
    "depends": [
        "stock",
    ],
    "author": "AvanzOSC,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "category": "Inventory, Logistic, Storage",
    "website": "http://github.com/OCA/stock-logistics-workflow",
    "summary": "More filters for inventory adjustments",
    "data": [
        "views/stock_inventory_view.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
    "license": 'AGPL-3',
}
