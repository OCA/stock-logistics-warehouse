# Copyright 2020 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request Partner",
    "summary": "Allow to define partner in Stock Request",
    "version": "14.0.1.0.1",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": ["stock_request"],
    "data": [
        "views/stock_request_views.xml",
        "views/stock_request_order_views.xml",
    ],
}
