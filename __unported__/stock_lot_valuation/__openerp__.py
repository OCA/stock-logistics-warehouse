# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Lot Valuation",
    'version': '0.1',
    'category': 'Warehouse Management',
    'description': """
Stock valuation (standard or average price, ...) based on lots.
This module extends standard stock valuation (based on products).
Valuing lots allows to have different costs for different lots of the same
product.

Usage
-----
Set the 'Lot valuation' flag on product form (used for real time valuation).
As for products, lots have 'cost' and 'costing method' fields. Also, a
'Change Standard Price' wizard is available.
""",
    'author': 'Agile Business Group',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['stock'],
    "data": [
        "wizard/stock_change_standard_price_view.xml",
        "product_view.xml",
        "stock_view.xml",
    ],
    "demo": [],
    'test': [
        'test/stock.yml',  # TODO cover user interface operations
    ],
    "active": False,
    'installable': False
}
