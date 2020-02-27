# -*- coding: utf-8 -*-
# Copyright 2016-18 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Generate Putaway from Inventory",
    "summary": "generate Putaway locations per Product deduced from inventory",
    "version": "10.0.1.0.1",
    "author": "Akretion",
    "category": "Warehouse",
    "depends": ["stock_putaway_product"],
    "license": "AGPL-3",
    "data": [
        "views/stock_inventory.xml",
    ],
    'installable': True,
}
