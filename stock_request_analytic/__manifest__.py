# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request Analytic",
    "summary": "Internal request for stock",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Analytic",
    "depends": ["stock_request", "stock_analytic"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_request_views.xml",
        "views/stock_request_order_views.xml",
        "views/analytic_views.xml",
    ],
    "installable": True,
}
