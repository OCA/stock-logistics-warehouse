# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Orderpoint Move Link",
    "summary": "Link Reordering rules to stock moves",
    "version": "12.0.1.1.0",
    "license": "LGPL-3",
    "website": "https://github.com/stock-logistics-warehouse",
    "author": "Eficent, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_move_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
