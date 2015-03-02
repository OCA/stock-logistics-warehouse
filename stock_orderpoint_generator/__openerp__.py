# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher, Matthieu Dietrich (Camptocamp)
#    Copyright 2012-2014 Camptocamp SA
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

{'name': 'Order point generator',
 'summary': 'Mass configuration of stock order points',
 'version': '1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'easy',
 'website': "http://www.camptocamp.com",
 'depends': ['procurement'],
 'description': """
Order point generator
=====================

Add a wizard to configure order points for multiple products in one go.

Contributors
------------

 * Yannick Vaucher <yannick.vaucher@camptocamp.com>
 * Matthieu Dietrich <matthieu.dietrich@camptocamp.com>

""",
 'demo': [],
 'data': ["wizard/orderpoint_generator_view.xml",
          "security/ir.model.access.csv",
          ],
 'test': ['test/orderpoint_generator.yml'],
 'installable': True,
 'auto_install': False,
 }
