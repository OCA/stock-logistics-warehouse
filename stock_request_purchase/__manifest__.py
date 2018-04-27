# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request Purchase",
    "summary": "Internal request for stock",
    "version": "11.0.2.0.1",
    "license": "LGPL-3",
    "website": "https://github.com/stock-logistics-warehouse",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": [
        "stock_request",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_request_views.xml",
        "views/stock_request_order_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    'auto_install': True,
}
