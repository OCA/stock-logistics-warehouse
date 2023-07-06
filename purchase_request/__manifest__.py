# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "16.0.1.0.0",
    "summary": "Use this module to have notification of requirements of "
    "materials and/or external services and keep track of such "
    "requirements.",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["purchase_stock"],
    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/purchase_request_sequence.xml",
        "data/purchase_request_data.xml",
        "reports/report_purchase_request.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_request_line_view.xml",
        "views/purchase_request_report.xml",
        "views/product_template.xml",
        "views/purchase_order_view.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],
    "demo": ["demo/purchase_request_demo.xml"],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
