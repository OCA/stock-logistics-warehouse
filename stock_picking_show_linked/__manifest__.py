# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.
{
    "name": "Stock Picking Show Linked",
    "summary": """
       This addon allows to easily access related pickings
       (in the case of chained routes) through a button
       in the parent picking view.
    """,
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": [
        "stock",
    ],
    "data": ["views/stock_picking.xml"],
    "license": "AGPL-3",
    "installable": True,
}
