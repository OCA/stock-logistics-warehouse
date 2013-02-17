# -*- encoding: utf-8 -*-
##############################################################################
#
#    Improved reordering rules for OpenERP
#    Copyright (C) 2012 Sergio Corato (<http://www.icstools.it>)
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
    'name': 'Improved reordering rules',
    'version': '0.1',
    'category': 'Tools',
    'description': """
    This module allows to improve reordering rules of stock module.""",
    'author': 'Sergio Corato',
    'website': 'http://www.icstools.it',
    'depends': ['procurement','sale',],
    'init_xml': [],
    'update_xml': ['stock_reord_rule_view.xml',],
    'demo_xml' : [],
    'data': ['cron_data.xml',],
    'images': [],
    'active': False,
    'installable': True,
}
