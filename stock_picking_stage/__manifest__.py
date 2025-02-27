# Copyright 2025 Camptocamp SA
# @author: Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Stock Picking Stages",
    "version": "18.0.1.0.0",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": ["stock"],
    "maintainers": ["imlopes"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_view.xml",
        "views/stock_picking_stage_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_picking_stage/static/src/components/environment_ribbon/*",
        ],
    },
    "installable": True,
}
