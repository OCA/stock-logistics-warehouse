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
    "name": "Exhaustive Stock Inventories",
    "version": "1.1",
    "depends": ["stock"],
    "author": u"Numérigraphe",
    "category": "Warehouse Management",
    "description": """
Let users make exhaustive Inventories
=====================================

Standard Physical Inventories in OpenERP only contain a generic list of
products by locations, which is well suited to partial Inventories and simple
warehouses. When the a standard Inventory is confirmed, only the products in
the inventory are checked. If a Product is present in the computed stock and
not in the recorded Inventory, OpenERP will consider that it remains unchanged.

But for exhaustive inventories in complex warehouses, it is not practical:
 - you want to avoid Stock Moves to/from these Locations while counting goods
 - you must make sure all the locations you want have been counted
 - you must make sure no other location has been counted by mistake
 - you want the computed stock to perfectly match the inventory when you
   confirm it.

This module lets choose whether an Physical Inventory is exhaustive or
standard.
For an exhaustive Inventory:
 - in the state "Draft" you define the Location where goods must be counted.
 - the new Inventory status "Open" lets you indicate that the list of Locations
   is final and you are now counting the goods.
   In that status, no Stock Moves can be recorded in/out of the Inventory's
   Locations.
 - if the Location or some of it's children have not been entered in the
   Inventory Lines, OpenERP warns you when you confirm the Inventory.
 - only the Inventory's Location or its children can be entered in the
   Inventory Lines.
 - every good that is not in the Inventory Lines is considered lost, and gets
   moved out of the stock when you confirm the Inventory.
""",
    "data": [
        "wizard/stock_confirm_uninventoried_location.xml",
        "stock_inventory_location_view.xml",
        "wizard/stock_fill_location_inventory_view.xml",
    ],
    "test": [
        "tests/inventory_standard_test.yml",
        "tests/inventory_exhaustive_test.yml",
        "tests/inventory_future_test.yml",
    ],
    "images": [
        "images/inventory_form.png",
        "inventory_empty_locations.png",
        "images/move_error.png",
        "images/location_locked.png",
        "images/future_inventory.png",
    ],
    "demo": ["stock_inventory_location_demo.xml"]
}
