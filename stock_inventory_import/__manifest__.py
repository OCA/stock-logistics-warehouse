# -*- coding: utf-8 -*-
# (c) 2015 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock Inventory Import from CSV file",
    "version": "10.0.1.0.0",
    "category": "Generic Modules",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa",
    "website": "https://odoo-community.org/",
    "depends": [
        "stock",
        "stock_inventory_line_price"
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_inventory_view.xml",
        "views/inventory_view.xml",
    ],
    "installable": True,
}
