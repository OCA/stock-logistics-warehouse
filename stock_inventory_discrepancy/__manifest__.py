# Copyright 2017-2020 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Discrepancy",
    "summary": "Adds the capability to show the discrepancy of every line in "
    "an inventory and to block the inventory validation when the "
    "discrepancy is over a user defined threshold.",
    "version": "16.0.1.2.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": [
        "security/stock_inventory_discrepancy_security.xml",
        "security/ir.model.access.csv",
        "views/stock_quant_view.xml",
        "views/stock_warehouse_view.xml",
        "views/stock_location_view.xml",
        "views/res_config_settings_view.xml",
        "wizards/confirm_discrepancy_wiz.xml",
    ],
    "license": "AGPL-3",
    "post_load": "post_load_hook",
    "installable": True,
    "application": False,
}
