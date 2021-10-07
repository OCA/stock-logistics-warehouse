# Copyright 2017-2021 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Exclude Sublocation",
    "summary": "Allow to perform inventories of a location without including "
    "its child locations.",
    "version": "14.0.1.0.1",
    "development_status": "Mature",
    "author": "ForgeFlow, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": ["views/stock_inventory_view.xml"],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
