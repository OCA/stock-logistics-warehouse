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
    'name': 'Quotations in quantity available to promise',
    'version': '2.0',
    'author': u'Numérigraphe SÀRL',
    'category': 'Hidden',
    'depends': [
        'stock_available',
        'sale_order_dates',
        'sale_stock',
    ],
    'description': """
This module computes the quoted quantity of the Products, and subtracts it from
the quantities available to promise .

"Quoted" is defined as the sum of the quantities of this product in Quotations,
taking the context's shop or warehouse into account.""",
    'data': [
        'product_view.xml',
    ],
    'test': [
        'test/quoted_qty.yml',
    ],
    'license': 'AGPL-3',
}
