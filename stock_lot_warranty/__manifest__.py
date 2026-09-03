# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Lot Warranty",
    "version": "19.0.1.0.0",
    "summary": "Adds customer warranty and vendor warranty date"
    " fields in the lot model.",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock", "product_warranty"],
    "data": [
        "views/stock_lot_views.xml",
    ],
    "installable": True,
    "application": False,
}
