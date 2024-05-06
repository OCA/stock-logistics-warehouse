# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Reservation Date Show",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "maintainer": ["JordiMForgeFlow"],
    "category": "Warehouse Management",
    "summary": "Display reservation date of stock moves",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "application": False,
}
