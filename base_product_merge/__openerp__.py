# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Guewen Baconnier (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    "name" : "Base Products Merge",
    "version" : "1.0",
    "author" : "Camptocamp",
    "category" : "Generic Modules/Base",
    "description":"""
To merge 2 products, select them in the list view and execute the Action "Merge Products".

The selected products are deactivated and a new one is created with :
- When a value is the same on each resources : the value
- When a value is different between the resources : you can choose the value to keep in a selection list
- When a value is set on a resource and is empty on the second one : the value is set on the resource
- All many2many relations of the 2 resources are created on the new resource.
- All the one2many relations (invoices, sale_orders, ...) are updated in order to link to the new resource.

""",
    "website": "http://camptocamp.com",
    "depends" : ['product'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "wizard/base_product_merge_view.xml",
    ],
    "active": False,
    "installable": False
}
