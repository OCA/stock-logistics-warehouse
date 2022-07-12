# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory User",
    "summary": "Add rule to allow only user of an inventory to modify it.",
    "version": "14.0.1.0.1",
    "development_status": "Mature",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": [
        "views/stock_inventory.xml",
        "security/ir_rule.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
