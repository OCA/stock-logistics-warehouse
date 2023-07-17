# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Reservation Area",
    "summary": "Stock reservations on areas (group of locations)",
    "version": "16.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "complexity": "normal",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_reserve_area_security.xml",
        "views/stock_reserve_area_views.xml",
        "views/stock_move_reserve_area_line_views.xml",
        "views/stock_location_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],
    "auto_install": False,
    "installable": True,
    "post_init_hook": "post_init_hook",
    "pre_init_hook": "pre_init_hook",
}
