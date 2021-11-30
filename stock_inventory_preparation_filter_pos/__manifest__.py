# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Inventory Preparation Filters POS",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Add POS category filter on inventory adjustments",
    "depends": ["stock_inventory_preparation_filter", "point_of_sale"],
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "category": "Inventory, Logistic, Storage",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "data": ["views/stock_inventory.xml"],
    "installable": True,
}
