# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2010-2012 Camptocamp SA
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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
#


{
    "name": "Immediately Usable Stock Quantity",
    "version": "1.0",
    "depends": ["product", "stock", ],
    "author": "Camptocamp",
    "license": "AGPL-3",
    "description": """
Compute the immediately usable stock.
Immediately usable is computed : Quantity on Hand - Outgoing Stock.
""",
    "website": "http://tinyerp.com/module_account.html",
    "category": "Generic Modules/Stock",
    "data": ["product_view.xml", 
             ],
    "active": False,
    "installable": True
}
