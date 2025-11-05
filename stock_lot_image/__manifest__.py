# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Lot Image",
    "version": "18.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_lot_image_views.xml",
        "views/stock_lot_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_lot_image/static/src/scss/stock_lot_image_backend.scss",
        ],
    },
    "maintainers": ["victoralmau"],
}
