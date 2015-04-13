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
    "name": "Stock Inventory Import from CSV file",
    "version": "1.0",
    "category": "Generic Modules",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "website": "http://www.odoomrp.com",
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_inventory_view.xml",
        "views/inventory_view.xml",
    ],
    "installable": True,
}
