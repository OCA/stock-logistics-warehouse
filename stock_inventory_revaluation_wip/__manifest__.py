# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Inventory Revaluation WIP",
    "summary": "Adds impacted BoM's workcenter products to cost adjustments.",
    "version": "14.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Stock",
    "license": "AGPL-3",
    "depends": ["stock_inventory_revaluation_mrp"],
    "data": [
        "views/cost_adjustment_detail.xml",
    ],
    "maintainers": ["patrickrwilson"],
    "application": False,
    "installable": True,
    "development_status": "Beta",
}
