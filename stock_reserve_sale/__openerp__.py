# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

{'name': 'Stock Reserve Sale',
 'version': '0.1',
 'author': 'Camptocamp',
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'normal',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Stock Reserve Sale
==================

Allows to create stock reservation for a quotation before it is
confirmed.  The reservation might have a validity date and in any
case the reservations are lifted when the quotation is canceled or
confirmed.
""",
 'depends': ['sale_stock',
             'stock_reserve',
             ],
 'demo': [],
 'data': ['wizard/sale_stock_reserve_view.xml',
          'view/sale.xml',
          ],
 'auto_install': False,
 'test': [],
 'installable': True,
 }
