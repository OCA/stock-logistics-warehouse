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
    "name": "Exhaustive and hierarchical Stock Inventories",
    "version": "1.1",
    "author": u"Numérigraphe",
    "category": "Hidden",
    "description": """
Make exhaustive Inventories aware of their Sub-Inventories.
===========================================================

This module allows an inventory to contain a general Location,
and it's sub-inventories to contain some of it's sub-Locations.
It will prevent you from setting the Inventories and sub-Inventories
in inconsistent status.

This module will be installed automatically if the modules
"stock_inventory_location" and "stock_inventory_hierarchical" are both
installed.
You must keep this module installed to ensure proper functioning.

    """,
    "data": [
        "inventory_hierarchical_location_view.xml",
        "wizard/generate_inventory_view.xml",
    ],
    "test": ["tests/inventory_hierarchical_location_test.yml"],
    "demo": ["inventory_hierarchical_location_demo.xml"],
    "depends": ["stock_inventory_hierarchical", "stock_inventory_location"],
    "auto_install": True,
}
