# Copyright 2023 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Request Purchase Request",
    "summary": """
        Stock Request Purchase Request""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock_request",
        "purchase_request",
    ],
    "data": [
        #     'views/stock_rule.xml',
        "views/stock_request.xml",
        "views/stock_request_order.xml",
        #     'views/purchase_request_line.xml',
        "views/purchase_request.xml",
    ],
    "demo": [],
}
