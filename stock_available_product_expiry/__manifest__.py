# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Expiry Available',
    'summary': """
        Allows to get product availability taking into account lot removal date
        """,
    'version': '10.0.1.0.3',
    'development_status': 'Alpha',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'depends': [
        'stock',
        'stock_available',
        'product_expiry',
        'web',
    ],
    'data': [
        'security/stock_scrap_expired_line.xml',
        'security/stock_scrap_expired.xml',
        'views/stock_scrap_expired_line.xml',
        'views/stock_scrap_expired.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'views/stock_quant.xml',
        'views/res_config.xml',
        'views/stock_available_product_expiry.xml',
        'reports/stock_scrap_expired.xml',
        'data/ir_sequence_data.xml',
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
}
