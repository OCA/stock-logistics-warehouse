# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Packaging",
    "version": "10.0.1.0.1",
    "author": 'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    "category": "Warehouse",
    "website": "http://www.acsone.eu",
    'summary': "In sale, use uom's package",
    "depends": [
        "sale_stock",
        "packaging_uom",
    ],
    "data": [
        "views/procurement_rule.xml",
        "views/sale_order_line_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
