# Copyright 2019 NaN (http://www.nan-tic.com) - Àngel Àlvarez
# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock product Pack',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'summary': 'This module allows you to get the right available quantities '
               'of the packs',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'author': 'NaN·tic, '
              'ADHOC SA, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'maintainers': ['ernestotejeda'],
    'license': 'AGPL-3',
    'depends': [
        'product_pack',
        'stock',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
