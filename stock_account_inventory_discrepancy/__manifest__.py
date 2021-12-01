# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Account Inventory Discrepancy",
    "summary": "Adds the capability to show the value discrepancy of every "
               "line in an inventory and to block the inventory validation "
               "when the discrepancy is over a user defined threshold.",
    "version": "12.0.1.0.0",
    "author": "ForgeFlow, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_inventory_discrepancy"],
    "data": [
        "views/stock_inventory_view.xml",
        "views/stock_warehouse_view.xml",
        "views/stock_location_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
