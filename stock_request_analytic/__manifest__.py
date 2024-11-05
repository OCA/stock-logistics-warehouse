# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Request Analytic",
    "summary": "Internal request for stock",
    "version": "15.0.1.1.1",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["AaronHForgeFlow"],
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
