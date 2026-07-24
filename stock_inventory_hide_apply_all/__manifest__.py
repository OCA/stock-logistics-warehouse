# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Inventory Hide Apply All",
    "summary": "Hide the 'Apply All' button on the inventory adjustment list",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Quartile, Odoo Community Association (OCA)",
    "maintainers": ["smorita7749"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/security.xml",
        "views/stock_quant_views.xml",
    ],
}
