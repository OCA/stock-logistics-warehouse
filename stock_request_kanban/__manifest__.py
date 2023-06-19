# Copyright 2018-22 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request kanban",
    "version": "15.0.1.1.1",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "summary": "Adds a stock request order, and takes stock requests as lines",
    "depends": ["stock_request", "barcodes"],
    "data": [
        "data/stock_request_sequence_data.xml",
        "report/report_paper_format.xml",
        "wizard/wizard_stock_inventory_kanban_views.xml",
        "wizard/wizard_stock_request_kanban_views.xml",
        "wizard/wizard_stock_request_order_kanban_views.xml",
        "views/stock_request_order_views.xml",
        "views/stock_request_kanban_views.xml",
        "views/stock_inventory_kanban_views.xml",
        "views/stock_request_menu.xml",
        "views/stock_request_views.xml",
        "views/product_views.xml",
        "report/stock_request_kanban_templates.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_request_kanban/static/src/js/stock_request_kanban_scan_controller.esm.js",
            "stock_request_kanban/static/src/js/stock_request_kanban_scan_view.esm.js",
        ],
        "web.assets_qweb": [
            "stock_request_kanban/static/src/xml/stock_request_kanban_scan.xml",
        ],
    },
    "installable": True,
    "application": False,
}
