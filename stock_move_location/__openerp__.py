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
    "name" : "Move Stock Location",
    "version" : "1.0",
    "author" : "Julius Network Solutions,Odoo Community Association (OCA)",
    "description" : """

Presentation:

This module allows to move all stock in a stock location to an other one.
And adds fields and buttons to advance in Physical Inventories.

""",
    "website" : "http://www.julius.fr",
    "depends" : [
        "stock",
        "stock_barcode_reader",
    ],
    "category" : "Customs/Stock",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    'stock_view.xml',
                    'stock_move_sequence.xml',
                    'wizard/move_location_view.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
