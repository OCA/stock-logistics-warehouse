# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'stock lot sale tracking',
    'summary': 'This addon allows to retrieve all customer '
    'deliveries impacted by a lot',
    'version': '10.0.1.0.0',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-warehouse/tree/10.0'
               '/stock_lot_sale_tracking',
    'license': 'AGPL-3',
    'category': 'Stock',
    'depends': [
        'stock',
        'sale_stock'
    ],
    'data': [
        "security/security.xml",
        "report/stock_lot_sale_report.xml",
    ],
    'installable': True,
}
