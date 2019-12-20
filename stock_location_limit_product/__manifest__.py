# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Stock Location Limit Product',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators, Odoo Community Association (OCA),',
    'website': "https://github.com/OCA/stock-logistics-warehouse",
    'summary': """Add a limit by product quantity on a stock location.
                This limit can later be used to track the capacity
                available of the location.""",
    'category': 'Warehouse',
    'development_status': 'Stable',
    'maintainers': ['max3903'],
    'depends': [
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/stock_location_view.xml',
    ],
    'installable': True,
}
