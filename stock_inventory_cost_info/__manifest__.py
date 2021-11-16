# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Inventory Cost Info",
    "summary": "Shows the cost of the inventory adjustments",
    "version": "14.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": ["views/stock_inventory_views.xml", "views/report_stockinventory.xml"],
    "pre_init_hook": "pre_init_hook",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
