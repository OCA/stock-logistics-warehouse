# Copyright 2019 Open Source Integrators
# Copyright 2019-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Request Submit",
    "summary": "Add submit state on Stock Requests",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": ["stock_request"],
    "data": ["views/stock_request_order_views.xml", "views/stock_request_views.xml"],
    "installable": True,
    "uninstall_hook": "uninstall_hook",
}
