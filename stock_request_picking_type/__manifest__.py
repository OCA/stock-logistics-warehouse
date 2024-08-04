# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request Picking Type",
    "summary": "Add Stock Requests to the Inventory App",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-request",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "depends": ["stock_request"],
    "data": [
        "data/stock_picking_type.xml",
        "views/stock_request_order_views.xml",
        "views/stock_warehouse_views.xml",
        "views/stock_picking_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
