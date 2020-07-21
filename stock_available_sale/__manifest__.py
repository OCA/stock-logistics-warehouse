# Copyright 2014 Numérigraphe SARL
# Copyright 2017 Tecnativa - David  Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Quotations in quantity available to promise',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Numérigraphe, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'category': 'Stock',
    'depends': [
        'stock_available',
        'sale',
        'sale_stock',
    ],
    'data': [
        'views/product_template_view.xml',
    ],
    'installable': True,
}
