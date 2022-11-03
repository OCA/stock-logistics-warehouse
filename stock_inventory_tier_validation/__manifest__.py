# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Inventory Adjustment Tier Validation",
    "summary": "Extends the functionality of Adjustments to "
    "support a tier validation process.",
    "version": "14.0.1.0.0",
    "category": "Stock Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainers": ["patrickrwilson"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock", "base_tier_validation"],
    "data": ["views/stock_inventory_views.xml"],
}
