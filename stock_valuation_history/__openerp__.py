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
    "name": "Stock valuation history",
    "version": "2.0",
    "depends": ["stock"],
    "author": u"Numérigraphe",
    "category": "Pricing",
    "description": """
Record Stock Valuation
======================
* Adds a wizard to record the current Stock Valuation of a location (with
  sub-locations)
* Adds an API to record the Stock Valuation by Product ID or by search domain.
  The location, warehouse or shop can be set in the context.
* Proposes a scheduled task to record the valuation once a week.

This module was previously named 'stock_valuation_history' in OpenERP v6.0.
""",
    "init_xml": [
        "stock_valuation_history_data.xml",
    ],
    "data": [
        "stock_valuation_history_view.xml",
        "wizard/compute_stock_valuation_wizard_view.xml",
        "security/ir.model.access.csv",
    ],
    "test": [
        "stock_valuation_history_test.yml",
    ],
    "demo": [
        "stock_valuation_history_demo.xml"
    ]
}
