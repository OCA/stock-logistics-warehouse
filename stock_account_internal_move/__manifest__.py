# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
{
    'name': """Stock Account Internal Move""",
    'summary': """Allows tracking moves between internal locations"""
               """ via accounts.""",
    'category': "Warehouse Management",
    'version': "11.0.1.0.0",
    'author': "Camptocamp,"
              " Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/stock-logistics-warehouse",
    'license': "AGPL-3",
    'depends': [
        'stock_account',
    ],
    'data': [
        'views/stock_location.xml',
    ],
    'development_status': 'Production/Stable',
    'maintainers': [
        'arkostyuk',
        'max3903',
    ],
}
