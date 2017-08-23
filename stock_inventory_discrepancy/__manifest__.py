# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Discrepancy",
    "summary": "Adds the capability to show the discrepancy of every line in "
               "an inventory and to block the inventory validation when the "
               "discrepancy is over a user defined threshold.",
    "version": "10.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        'views/stock_inventory_view.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_location_view.xml',
        'security/stock_inventory_discrepancy_security.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
