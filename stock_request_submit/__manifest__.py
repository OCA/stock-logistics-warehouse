# Copyright 2019 Open Source Integrators
# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Request Submit",
    "summary": "Add submit state on Stock Requests",
    "version": "12.0.1.0.2",
    "license": "LGPL-3",
    "website": "https://github.com/stock-logistics-warehouse",
    "author": "Open Source Integrators, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse",
    'depends': ['stock_request'],
    'data': [
        'views/stock_request_order_views.xml',
        'views/stock_request_views.xml',
    ],
    "installable": True,
    'uninstall_hook': 'uninstall_hook',
}
