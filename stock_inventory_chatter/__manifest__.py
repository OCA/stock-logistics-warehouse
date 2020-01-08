# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Chatter",
    "version": "13.0.1.0.0",
    "author": "ForgeFlow," "Odoo Community Association (OCA)",
    "development_status": "Mature",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "summary": "Log changes being done in Inventory Adjustments",
    "depends": ["stock"],
    "data": ["data/stock_data.xml", "views/stock_inventory_view.xml"],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
