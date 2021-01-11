# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request",
    "summary": "Internal request for stock",
    "version": "12.0.1.5.0",
    "license": "LGPL-3",
    "website": "https://github.com/stock-logistics-warehouse",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse",
    "depends": [
        "stock",
    ],
    "data": [
        "security/stock_request_security.xml",
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/stock_request_views.xml",
        "views/stock_request_allocation_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_request_order_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_request_menu.xml",
        "data/stock_request_sequence_data.xml",
    ],
    "installable": True,
}
