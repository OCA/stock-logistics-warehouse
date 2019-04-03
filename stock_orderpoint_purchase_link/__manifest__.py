# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Orderpoint Purchase Link",
    "summary": "Link Reordering rules to purchase orders",
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": [
        "stock_orderpoint_move_link",
        "purchase_stock",
    ],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
