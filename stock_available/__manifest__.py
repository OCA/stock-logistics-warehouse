# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock available to promise',
    'version': '11.0.1.1.1',
    "author": "Numérigraphe, Sodexis, Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'depends': ['stock'],
    'license': 'AGPL-3',
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    'data': [
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
