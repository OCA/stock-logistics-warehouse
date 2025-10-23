# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vertical Lift",
    "summary": "Provides the core for integration with Vertical Lifts",
    "version": "18.0.1.2.2",
    "category": "Stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "barcodes",
        "base_sparse_field",
        "stock_location_tray",  # OCA/stock-logistics-warehouse
        "web_notify",  # OCA/web
    ],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "demo": [
        "demo/stock_location_demo.xml",
        "demo/vertical_lift_shuttle_demo.xml",
        "demo/product_demo.xml",
        "demo/stock_quant_demo.xml",
        "demo/stock_picking_demo.xml",
    ],
    "data": [
        "views/stock_location_views.xml",
        "views/stock_move_line_views.xml",
        "views/vertical_lift_shuttle_views.xml",
        "views/vertical_lift_operation_base_views.xml",
        "views/vertical_lift_operation_pick_views.xml",
        "views/vertical_lift_operation_put_views.xml",
        "views/vertical_lift_operation_inventory_views.xml",
        "views/shuttle_screen_templates.xml",
        "views/res_config_settings_views.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_vertical_lift/static/src/scss/vertical_lift.scss",
            "stock_vertical_lift/static/src/js/vertical_lift.esm.js",
            "stock_vertical_lift/static/src/js/web_client.esm.js",
        ]
    },
    "installable": True,
    "development_status": "Alpha",
}
