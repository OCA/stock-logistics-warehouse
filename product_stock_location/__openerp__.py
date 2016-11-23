# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Stock Location",
    "version": "8.0.1.0.0",
    "depends": [
        "stock",
        "stock_warehouse_orderpoint_stock_info"
    ],
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Warehouse",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "security/stock_security.xml",
        "views/product_stock_location_view.xml",
        "views/product_view.xml"
    ],
    'pre_init_hook': 'pre_init_hook',
    "installable": True,
    "auto_install": False,
}
