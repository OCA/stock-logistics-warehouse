# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Location State",
    "summary": "Verify that all locations are counted.",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["bguillot"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_inventory"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_inventory.xml",
        "views/stock_inventory_location.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
