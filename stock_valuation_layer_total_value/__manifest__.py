# Copyright 2022 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Valuation Layer Total Value",
    "summary": "Show total value on tree and form view",
    "version": "14.0.0.0.0",
    "development_status": "Production/Stable",
    "category": "stock",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Forgeflow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock_account"],
    "data": [
        "views/stock_valuation_layer.xml",
    ],
}
