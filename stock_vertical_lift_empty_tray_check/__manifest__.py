# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Vertical Lift Empty Tray Check",
    "summary": "Checks if the tray is actually empty.",
    "version": "14.0.1.0.0",
    "category": "Stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock", "stock_vertical_lift"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_setting_views.xml",
        "views/vertical_lift_operation_pick_zero_check_views.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
