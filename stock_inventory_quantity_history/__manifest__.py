# Copyright 2024 Akretion France (http://www.akretion.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Inventory Theoretical Quantity History",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Keep theoretical and real quantities history",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
}
