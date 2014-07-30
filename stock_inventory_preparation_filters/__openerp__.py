# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Extended Inventory Preparation Filters",
    "version": "1.0",
    "depends": [
        "stock",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Custom Module",
    "website": "http://www.odoomrp.com",
    "summary": "More filters for inventory adjustments",
    "description": """
    More preparation filters for inventories
    ========================================

    Includes more options for making an inventory out of:

        * Multiple products.
        * Products of a category.
        * Multiple lots

        It also allows to make an inventory based on scanned products, adding a
        line with product code and quantity
    """,
    "data": [
        "views/stock_inventory_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
