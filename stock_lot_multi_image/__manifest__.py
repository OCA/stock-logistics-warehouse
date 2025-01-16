# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Multiple Images in Stock Lot",
    "summary": """This module implements the possibility to
    have multiple images for a stock lot""",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "version": "16.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock",
        "base_multi_image",
    ],
    "data": [
        "views/stock_lot_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
