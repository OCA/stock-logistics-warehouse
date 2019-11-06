# Copyright (c) 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Requests Direction",
    "summary": "From or to your warehouse?",
    "version": "12.0.1.0.2",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Open Source Integrators, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse",
    "depends": [
        "stock_request",
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/stock_request_views.xml",
        "views/stock_request_order_views.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
