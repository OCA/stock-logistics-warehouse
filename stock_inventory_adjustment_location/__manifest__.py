# Copyright 2026 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Inventory Adjustment Location",
    "summary": "Allow choosing the inventory loss counterpart location "
    "when applying inventory adjustments.",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock_account"],
    "data": [
        "wizard/stock_inventory_adjustment_name_views.xml",
    ],
    "installable": True,
}
