# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
{
    "name": "Stock Batch Packaging Qty",
    "summary": "Add packaging fields in stock picking batch",
    "version": "16.0.1.0.1",
    "author": "Moduon, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_picking_batch", "stock_move_packaging_qty"],
    "data": [
        "views/stock_move_line_view.xml",
        "views/stock_move_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "autoinstall": True,
    "maintainers": ["EmilioPascual", "rafaelbn"],
}
