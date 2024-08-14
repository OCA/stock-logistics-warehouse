# Copyright 2024 Matt Taylor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Specific Identification Inventory Valuation",
    "summary": "Track value of specific items in inventory based on lot or serial number",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "stock",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Matt Taylor, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_account",
    ],
    "data": [
        "views/product_category_views.xml",
        "views/stock_valuation_layer_views.xml",
        "wizards/stock_valuation_layer_lot_revaluation_views.xml",
        "security/ir.model.access.csv",
    ],
}
