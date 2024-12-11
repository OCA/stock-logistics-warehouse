# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Stock Picking Show Linked",
    "summary": """
       This addon allows to easily access related pickings
       (in the case of chained routes) through a button
       in the parent picking view.
    """,
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": ["views/stock_picking.xml"],
    "license": "AGPL-3",
    "installable": True,
}
