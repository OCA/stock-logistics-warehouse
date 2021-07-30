# Copyright 2016-18 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Generate Putaway from Inventory",
    "summary": "Generate Putaway locations per Product deduced from Inventory",
    "version": "14.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock", "stock_location_children"],
    "license": "AGPL-3",
    "data": ["views/stock_inventory.xml"],
    "installable": True,
    "maintainers": ["pierrickbrun", "bealdav", "sebastienbeau", "kevinkhao"],
}
