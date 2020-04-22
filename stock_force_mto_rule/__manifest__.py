# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Francisco Fernández <ffernandez@planetatic.com>
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock force MTO rule',
    'version': '10.0.1.0.0',
    'category': 'Warehouse',
    'author': 'PlanetaTIC',
    'website': 'https://www.planetatic.com',
    'description': "Allows to force MTO rule in sale order lines",
    'depends': [
        'sale',
        'stock',
    ],
    'init_xml': [],
    'update_xml': [
        'views/sale_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'images': [],
}
