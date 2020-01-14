# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Request Employee',
    'summary': """
        Deliver Stock requests directly to employees""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'depends': [
        'stock_request',
        'hr',
    ],
    'data': [
        'data/stock_location.xml',
        'views/hr_employee.xml',
        'views/stock_request.xml',
        'views/stock_request_order.xml',
    ],
}
