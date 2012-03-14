# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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
	"name" : "Immediately Usable Stock Quantity",
	"version" : "1.0",
	"depends" : [
	             "base",
	             "product",
				 "stock",
				],
	"author" : "Camptocamp",
	"description": """Compute the immediately usable stock. Immediately usable is computed : Real Stock - Outgoing Stock. """,
	"website" : "http://tinyerp.com/module_account.html",
	"category" : "Generic Modules/Stock",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
	                "product_view.xml",
	               ],
	"active": False,
	"installable": True
}
