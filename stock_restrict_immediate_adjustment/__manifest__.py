# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Restrict Immediate Adjustment",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Restrict immediate stock adjustments from Stock On Hand view",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "views/stock_quant_views.xml",
    ],
    "installable": True,
    "application": False,
}
