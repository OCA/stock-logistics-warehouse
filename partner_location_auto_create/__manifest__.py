# © 2015 Savoir-faire Linux
# © 2018 brain-tec AG (Kumar Aberer <kumar.aberer@braintec-group.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Partner Location Auto Create',
    'version': '11.0.1.0.0',
    'author': 'brain-tec AG, Savoir-faire Linux,Odoo Community Association ('
              'OCA)',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'complexity': 'normal',
    'images': [],
    'website': 'http://www.savoirfairelinux.com',
    'depends': [
        'sale_stock',
    ],
    'demo': [],
    'data': [
        'views/res_partner_view.xml',
        'views/res_config_settings_view.xml',
        'views/stock_location_view.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'test': [],
    'auto_install': False,
    'installable': True,
}
