# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Reservation Area Mrp",
    "summary": "Stock reservations in Manufacturing Orders",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "complexity": "normal",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock_reserve_area", "mrp"],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "auto_install": False,
    "installable": True,
}
