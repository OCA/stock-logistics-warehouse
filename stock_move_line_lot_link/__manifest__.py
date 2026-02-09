# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Move Line Lot Link",
    "summary": "Display Lot/SN column on Detailed Operations to allow navigation.",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
}
