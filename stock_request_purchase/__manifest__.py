# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request Purchase",
    "summary": "Internal request for stock",
    "version": "12.0.1.1.3",
    "license": "LGPL-3",
    "website": "https://github.com/stock-logistics-warehouse",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse",
    "depends": [
        "stock_request",
        "purchase_stock",
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
