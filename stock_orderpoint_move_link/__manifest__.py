# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Orderpoint Move Link",
    "summary": "Link Reordering rules to stock moves",
    "version": "11.0.1.1.1",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_move_views.xml",
    ],
    "installable": True,
    'auto_install': False,
}
