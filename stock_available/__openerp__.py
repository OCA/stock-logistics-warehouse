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
    'name': 'Stock available to promise',
    'version': '2.0',
    'author': u'Numérigraphe',
    'category': 'Warehouse',
    'depends': ['stock'],
    'description': """
Stock available to promise
==========================
This module proposes several options to compute the quantity available to
promise for each product.
This quantity is based on the projected stock and, depending on the
configuration, it can account for various data such as sales quotations or
immediate production capacity.
This can be configured in the menu Settings > Configuration > Warehouse.
""",
    'license': 'AGPL-3',
    'data': [
        'product_view.xml',
        'res_config_view.xml',
    ]
}
