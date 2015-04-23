# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Stock internal transfer transit',
    'version': '1.0',
    'category': '',
    'summary': "Process internal transfers using a dedicated stock location.",
    'description': """
Customize wizard from 'stock_internal_transfer' module to process internal
transfers between stock locations using a dedicated 'transit' stock location.
Each transfer creates two pickings and corresponding moves.
First picking is to move goods from their source stock location into the
transit stock location (truck, ship etc) for transport.
Second picking is to move goods from transit stock location to
destination stock location on arrival.
""",
    'author': 'initOS GmbH & Co. KG, Odoo Community Association (OCA)',
    'website': 'http://www.initos.com',
    'depends': [
        'stock_internal_transfer',
    ],
    'data': [
        'stock_transit.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [
    ],
    'css': [
    ],
    'js': [
    ],
    'qweb': [
    ],
}
