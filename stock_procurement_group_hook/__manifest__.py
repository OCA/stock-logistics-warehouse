# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Procurement Group Hook",
    "summary": "Adds Hook to Procurement Group run method.",
    "version": "15.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "post_load": "post_load_hook",
}
