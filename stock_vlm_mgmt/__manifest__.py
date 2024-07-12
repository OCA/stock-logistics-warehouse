# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Vertical Lift Module management",
    "summary": "Light self contained alternative for VLM integrations",
    "version": "16.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "maintainers": ["chienandalu"],
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["stock", "base_sparse_field"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_location_vlm_tray_views.xml",
        "views/stock_location_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_quant_views.xml",
        "views/stock_vlm_task_views.xml",
        "views/stock_quant_vlm_views.xml",
        "views/stock_location_tray_type_views.xml",
        "wizards/stock_vlm_task_action_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_vlm_mgmt/static/src/scss/stock_vlm_mgmt.scss",
            "stock_vlm_mgmt/static/src/js/**/*",
        ],
    },
}
