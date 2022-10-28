# Copyright 2018 Camptocamp SA
# Copyright 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Putaway strategy per product',
    'summary': 'Set a product location and put-away strategy per product',
    'version': '11.0.1.0.3',
    'category': 'Inventory',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'author': 'Apertoso N.V., '
              'Tecnativa, '
              'Camptocamp SA, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'stock_putaway_method'
    ],
    'data': [
        'views/product.xml',
        'views/product_putaway.xml',
        'security/ir.model.access.csv',
    ]
}
