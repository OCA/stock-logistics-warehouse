# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 initOS GmbH (<http://www.initos.com>).
#    Author Rami Alwafaie <rami.alwafaie at initos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Products Default Location',
    'version': '0.1',
    "author": "initos GmbH",
    "website": "http://www.initos.com",
    "license": "AGPL-3",
    "category": "",
    "description": """
This module allows to set a default location for the product
and fill this location automatically in stock move according to
the picking type.
    """,
    'depends': [
        'product',
        'stock',
    ],
    "data": [
        'product_view.xml',
        'stock_move_view.xml',
    ],
    'installable': True,
    'active': False,
}
