# Copyright 2020 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Stock Inventory Valuation by Location",
    "version": "12.0.1.0.0",
    "author": "Vauxoo, Odoo Community Association (OCA)",
    "summary": "Introduces an estimation of the value by location.",
    "depends": [
        "stock",
        "account",
    ],
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "data": [
        "views/stock_quant_views.xml",
    ],
    "installable": True,
    "application": False,
}
