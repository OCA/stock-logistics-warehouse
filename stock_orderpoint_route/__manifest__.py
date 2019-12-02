# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Stock Orderpoint Route",
    'summary': "Select a route for Reordering Rules",
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/stock-logistics-warehouse",
    'category': 'Warehouse Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_warehouse_orderpoint_views.xml',
        'views/stock_location_route_views.xml',
    ],
    'installable': True,
}
