# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Verification Request",
    "summary": "Adds the capability to request a Slot Verification when "
               "a inventory is Pending to Approve",
    "version": "10.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock_inventory_discrepancy",
                "mail"],
    "data": [
        'views/stock_slot_verification_request_view.xml',
        'views/stock_inventory_view.xml',
        'data/slot_verification_request_sequence.xml',
        'security/ir.model.access.csv',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
