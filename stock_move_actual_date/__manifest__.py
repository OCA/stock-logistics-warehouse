# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Move Actual Date",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Stock",
    "license": "AGPL-3",
    "depends": ["stock_account"],
    "data": [
        "security/stock_move_actual_date_security.xml",
        "views/stock_move_line_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_scrap_views.xml",
        "views/stock_valuation_layer_views.xml",
        "wizard/stock_quantity_history.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
