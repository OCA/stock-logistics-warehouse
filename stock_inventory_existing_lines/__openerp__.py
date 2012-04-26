# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    "name" : "Inventory Extended",
    "version" : "1.0",
    "author" : "Julius Network Solutions",
    "description" : """
    
Presentation:

This module adds a new field based on lines into the inventory
to know what are lines correctly in the system.

This module adds a new tab 'Lines' in Physical Inventories with correct lines of Stock Inventory Lines.
  
     """,
    "website" : "http://www.julius.fr",
    "depends" : [
         "stock",
    ],
    "category" : "Customs/Stock",
    "init_xml" : [],
    "demo_xml" : [],
    "images" : ['images/Inventory existing lines.png'],
    "update_xml" : [
        'stock_view.xml',
        "security/ir.model.access.csv",
    ],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
