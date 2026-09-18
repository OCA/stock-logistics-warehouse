# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Restriction",
    "summary": "Restrict inventory modifications to assigned users",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Inventory/Inventory",
    "depends": ["stock_inventory"],
    "data": [
        "security/ir_rule.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
