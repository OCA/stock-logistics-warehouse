# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

{'name': 'Stock Location Search Stock Quantities',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Warehouse Management',
 'depends': ['stock',
             ],
 'description': """
Stock Location Search Stock Quantities
======================================

Add search functions on Products' Real and Virtual Stock on Stock Locations.

The "Stock by Location" view that is accessed from a product shows the
list of locations, each one with the Real and Virtual Stock for the
product. However, there is no way to filter out the locations which
doesn't contain the product so the view is cluttered with a lot of
lines with a 0.0 quantity. This module adds search functions on the quantity
fields.

Also, by default, a filter hides the locations without quantity at all.

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['stock_location_view.xml',
          ],
 'test': ['test/location_search.yml',
          ],
 'installable': True,
 'auto_install': False,
 }
