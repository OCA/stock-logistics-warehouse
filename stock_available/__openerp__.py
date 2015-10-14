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
    'version': '8.0.2.0.0',
    "author": u"Numérigraphe,Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'depends': ['stock'],
    'license': 'AGPL-3',
    'data': [
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'views/res_config_view.xml',
    ]
    'installable': False,
}
