# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
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
##############################################################################

{
    "name": "Hierarchical Physical Inventory",
    "version": "1.1",
    "depends": ["stock"],
    "author": "Numérigraphe",
    "category": "Warehouse Management",
    "description": """
Hierarchical structure for Physical Inventories and sub-Inventories
===================================================================

This module adds a parent-child relationship between Physical Inventories, to
help users manage complex inventories.
Using several inventories, you can distribute the counting to several persons
and still keep a clear overview of global Inventory's status.

OpenERP will make sure the status of the Inventory and it's Sub-Inventories are
consistent.
""",
    "data": ["hierarchical_inventory_view.xml"],
    "test": ["test/hierarchical_inventory_test.yml"],
    "demo": ["hierarchical_inventory_demo.xml"],
    "images": [
        "inventory_form.png",
        "inventory_form_actions.png",
    ],
}
