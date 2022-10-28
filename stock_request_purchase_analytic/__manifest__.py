# Copyright 2017-2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Request Purchase Analytic",
    "summary": "Passes the analytic account from the stock request to the "
               "purchase order",
    "version": "11.0.1.0.2",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": [
        "stock_request_purchase",
        "stock_request_analytic",
    ],
    "installable": True,
    'auto_install': True,
}
