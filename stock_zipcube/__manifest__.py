# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Zipcube",
    "summary": "Implement interface with Bosche Zipcube devices "
    "for packaging measurement",
    "version": "13.0.1.1.0",
    "category": "Warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        # For the pop-up message to tell the user to refresh.
        "web_ir_actions_act_view_reload",
        # TODO: extract the common parts in a separate module to avoid pulling
        # unneeded external_dependencies
        "stock_cubiscan",
    ],
    "data": ["wizard/cubiscan_wizard.xml"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "installable": True,
    "development_status": "Alpha",
}
