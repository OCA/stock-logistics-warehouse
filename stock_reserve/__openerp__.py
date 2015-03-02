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

{'name': 'Stock Reservation',
 'summary': 'Stock reservations on products',
 'version': '0.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'normal',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Stock Reservation
=================

Allows to create stock reservations on products.

Each reservation can have a validity date, once passed, the reservation
is automatically lifted.

The reserved products are substracted from the virtual stock. It means
that if you reserved a quantity of products which bring the virtual
stock below the minimum, the orderpoint will be triggered and new
purchase orders will be generated. It also implies that the max may be
exceeded if the reservations are canceled.

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>

""",
 'depends': ['stock',
             ],
 'demo': [],
 'data': ['view/stock_reserve.xml',
          'view/product.xml',
          'data/stock_data.xml',
          'security/ir.model.access.csv',
          ],
 'auto_install': False,
 'test': ['test/stock_reserve.yml',
          ],
 'installable': True,
 }
