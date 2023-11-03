# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Quant Estimated Value",
    "summary": "Shows the cost of the quants",
    "version": "15.0.1.1.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": ["views/stock_inventory_views.xml"],
    "pre_init_hook": "pre_init_hook",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}
