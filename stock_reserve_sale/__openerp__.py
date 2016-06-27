# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier, Leonardo Pistone
#    Copyright 2013-2015 Camptocamp SA
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

{'name': 'Stock Reserve Sales',
 'version': '8.0.1.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'normal',
 'images': [],
 'website': "http://www.camptocamp.com",
 'depends': ['sale_stock',
             'stock_reserve',
             ],
 'demo': [],
 'data': ['wizard/sale_stock_reserve_view.xml',
          'view/sale.xml',
          'view/stock_reserve.xml',
          ],
 'test': ['test/sale_reserve.yml',
          'test/sale_line_reserve.yml',
          'test/sale_line_reserve_delete.yml',
          ],
 'installable': True,
 'auto_install': False,
 }
