# Copyright 2022-2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Valuation Layer Accounting Date",
    "category": "Stock",
    "version": "16.0.1.0.2",
    "author": "Quartile Limited, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": ["stock_account"],
    "data": [
        "views/stock_valuation_layer_views.xml",
        "wizard/stock_quantity_history.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
