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
    'name': 'Stock Inventory Import from CSV file',
    'version': "1.0",
    'category': "Generic Modules",
    'description': """
    Wizard to import Inventory from a CSV file
    The file must have at least 2 columns with "code" and "quantity" Head Keys.
    You can also add a third column with Key "location" to add product location
    (if not defined, default inventory location will be used)
    You can also add a fourth column with Key "lot" to add a product lot.
    """,
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",

    'contributors': ["Daniel Campos <danielcampos@avanzosc.es>"],
    'website': "http://www.avanzosc.com",
    'depends': ['stock'],
    'data': ['security/ir.model.access.csv',
             'wizard/import_inventory_view.xml',
             'views/inventory_view.xml'],
    'installable': True,
}
