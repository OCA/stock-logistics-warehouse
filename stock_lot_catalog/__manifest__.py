# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Stock Lot Catalog",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "views/stock_lot_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_lot_catalog/static/src/js/**/*",
            "stock_lot_catalog/static/src/stock_lot_catalog/**/*.js",
            "stock_lot_catalog/static/src/stock_lot_catalog/**/*.xml",
            "stock_lot_catalog/static/src/stock_lot_catalog/**/*.scss",
        ],
    },
    "maintainers": ["victoralmau"],
}
