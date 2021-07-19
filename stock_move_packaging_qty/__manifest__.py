# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Move Packaging Qty",
    "summary": "Add packaging fields in the stock moves",
    "version": "12.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_form_view.xml",
        "views/stock_move_tree_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
