# -*- coding: utf-8 -*-
###############################################################################
#
#    Module for OpenERP
#    Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Florian DA COSTA <florian.dacosta@akretion.com>
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
###############################################################################
{
    "name": "Stock Dynamic MTO",
    "version": "1.0",
    "category": "Stock",
    "description": """
Stock Dynamic MTO
======================
The purpose of the module is to give the possibility to a pull rule
make to order to act like a make to stock rule depending of the virtual
stock of a product.
""",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "http://www.akretion.com/",
    "depends": [
        "stock",
        ],
    "data": [
        "pull_rule_view.xml",
        ],
    "installable": True,
}
