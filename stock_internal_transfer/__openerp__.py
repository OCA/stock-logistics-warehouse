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
    'name': 'Stock internal transfer',
    'version': '0.1',
    'category': '',
    'summary': 'Wizard to simplify creation of internal stock transfers',
    'description': """
Wizard to simplify creation of internal transfers between stock locations.
Creates stock moves and pickings to transfer selected goods between two
stock locations.
""",
    'author': 'initOS GmbH & Co. KG',
    'website': 'http://www.initos.com',
    'depends': [
        'stock',
    ],
    'data': [
        'stock_internal_transfer_view.xml',
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
