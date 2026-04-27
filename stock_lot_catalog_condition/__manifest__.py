# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Stock Lot Catalog Condition",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock_lot_catalog", "stock_lot_condition"],
    "data": [
        "views/stock_lot_views.xml",
    ],
    "maintainers": ["victoralmau"],
}
