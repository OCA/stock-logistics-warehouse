# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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
    'name': 'Consider the production potential is available to promise',
    'version': '2.0',
    'author': u'Numérigraphe',
    'category': 'Hidden',
    'depends': ['stock_available', 'mrp'],
    'description': """
This module takes the potential quantities available for Products in account in
the quantity available to promise, where the "Potential quantity" is the
quantity that can be manufactured with the components immediately at hand,
following a single level of Bill of Materials.""",
    'data': [
        'product_view.xml',
    ],
    'test': [
        'test/potential_qty.yml',
    ],
    'license': 'AGPL-3',
}
