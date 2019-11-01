# Copyright 2019 Camptocamp (https://www.camptocamp.com)
{
    'name': "Stock Picking Zone",
    'summary': "Add extra routing operations for special locations",
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/stock-logistics-warehouse",
    'category': 'Warehouse Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'stock',
    ],
    'demo': [
        'demo/stock_location_demo.xml',
        'demo/stock_picking_type_demo.xml',
    ],
    'data': [
        'views/stock_location.xml',
    ],
    'installable': True,
    'development_status': 'Alpha',
}
