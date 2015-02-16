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

{'name': 'Stock Reserve Sales',
 'version': '0.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'normal',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Stock Reserve Sales
===================

Allows to create stock reservations for quotation lines before the
confirmation of the quotation.  The reservations might have a validity
date and in any case they are lifted when the quotation is canceled or
confirmed.

Reservations can be done only on "make to stock" and stockable products.

The reserved products are substracted from the virtual stock. It means
that if you reserved a quantity of products which bring the virtual
stock below the minimum, the orderpoint will be triggered and new
purchase orders will be generated. It also implies that the max may be
exceeded if the reservations are canceled.

If you want to prevent sales orders to be confirmed when the stock is
insufficient at the order date, you may want to install the
`sale_exception_nostock` module.

""",
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
          ],
 'installable': True,
 'auto_install': False,
 }
