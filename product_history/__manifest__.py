#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

{
    'name': 'Product - History',
    'version': '12.0.2.0.0',
    'category': 'Product',
    'author': 'Akretion,'
              'Druidoo',
    'website': 'http://druidoo.io',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'stock',
        'product_average_consumption',
        'queue_job',
    ],
    'data': [
        'security/product_history_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_view.xml',
        'views/product_history_view.xml',
        'views/product_template_view.xml',
        'data/function.xml',
        'data/cron.xml',
    ],
}
