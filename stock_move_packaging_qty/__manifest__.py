# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Packaging Qty",
    "summary": "Add packaging fields in the stock moves",
    "version": "16.0.1.4.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": [
        "views/report_stock_picking.xml",
        "views/stock_move_line_view.xml",
        "views/stock_move_view.xml",
        "views/stock_picking_form_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "maintainers": ["yajo"],
}
