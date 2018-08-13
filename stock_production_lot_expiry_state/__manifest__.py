# Copyright (C) 2018 - TODAY, Open Source Integrators
{
    'name': 'Lot/SN Expiry State',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'summary': 'Add a state field to expiring lot/SN',
    'category': 'Inventory',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'depends': ['stock'],
    'data': [
        'views/stock_production_lot_views.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': [
        'osimallen',
        'max3903',
    ]
}
