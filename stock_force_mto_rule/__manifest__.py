# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Francisco Fernández <ffernandez@planetatic.com>
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock force MTO rule',
    'version': '10.0.1.0.0',
    'category': 'Warehouse',
    'author': 'PlanetaTIC, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'description': "Allows to force MTO rule in sale order lines",
    'depends': [
        'sale_stock',
        'stock',
    ],
    'data': [
        'views/sale_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
