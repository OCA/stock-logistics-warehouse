# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Valuation Layer Inventory Filter",
    "summary": "Allows to filter Inventory Adjustments on Stock Valuation Layers",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_account",
    ],
    "data": [
        "views/stock_valuation_layer_view.xml",
    ],
}
