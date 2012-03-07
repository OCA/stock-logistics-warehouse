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
    "name" : "Stock On Hold Status",
    "version" : "1.0",
    "author" : "Julius Network Solutions",
    "description" : """ This Module allows to hold pickings.
    It's adding a button which holding the picking and workflow.
    You should use the sale_prepayment module to be automated with sale orders and invoices.
    """,
    "website" : "http://www.julius.fr",
    "depends" : [
                 "stock",
                 ],
    "category" : "Stock",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    'wizard/stock_invoice_onshipping_view.xml',
                    'stock_view.xml',
                    'stock_workflow.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
