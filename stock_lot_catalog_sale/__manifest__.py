# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Sale Stock Lot Catalog",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock_lot_catalog", "sale_order_lot_selection"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "maintainers": ["victoralmau"],
}
