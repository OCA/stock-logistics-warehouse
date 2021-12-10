# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vertical Lift",
    "summary": "Provides the core for integration with Vertical Lifts",
    "version": "14.0.1.1.1",
    "category": "Stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "barcodes",
        "base_sparse_field",
        "stock_location_tray",  # OCA/stock-logistics-warehouse
        "web_notify",  # OCA/web
        "web_ir_actions_act_view_reload",  # OCA/web
    ],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "demo": [
        "demo/stock_location_demo.xml",
        "demo/vertical_lift_shuttle_demo.xml",
        "demo/product_demo.xml",
        "demo/stock_inventory_demo.xml",
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
        "views/stock_vertical_lift_templates.xml",
        "views/shuttle_screen_templates.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
