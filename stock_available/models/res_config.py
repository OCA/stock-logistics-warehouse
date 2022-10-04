# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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

from openerp import models, fields


class StockConfig(models.TransientModel):
    """Add options to easily install the submodules"""
    _inherit = 'stock.config.settings'

    module_stock_available_immediately = fields.Boolean(
        string='Exclude incoming goods',
        help="This will subtract incoming quantities from the quantities "
             "available to promise.\n"
             "This installs the module stock_available_immediately.")

#    module_stock_available_sale = fields.Boolean(
#        string='Exclude goods already in sale quotations',
#        help="This will subtract quantities from the sale quotations from "
#             "the quantities available to promise.\n"
#             "This installs the modules stock_available_sale.\n"
#             "If the modules sale and sale_delivery_date are not "
#             "installed, this will install them too")

#    module_stock_available_mrp = fields.Boolean(
#        string='Include the production potential',
#        help="This will add the quantities of goods that can be "
#             "immediately manufactured, to the quantities available to "
#             "promise.\n"
#             "This installs the module stock_available_mrp.\n"
#             "If the module mrp is not installed, this will install it "
#             "too")
