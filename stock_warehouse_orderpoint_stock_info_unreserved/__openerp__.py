# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Reordering rules stock info unreserved",
    "version": "9.0.1.0.0",
    "depends": [
        "stock_warehouse_orderpoint_stock_info",
        "stock_available_unreserved"
    ],
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Warehouse",
    "license": "AGPL-3",
    "data": [
        "views/stock_warehouse_orderpoint_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
