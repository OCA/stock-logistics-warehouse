# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockConfig(models.TransientModel):
    """Add options to easily install the submodules"""
    _inherit = 'stock.config.settings'

    module_stock_available_immediately = fields.Boolean(
        string='Exclude incoming goods',
        help="This will subtract incoming quantities from the quantities "
             "available to promise.\n"
             "This installs the module stock_available_immediately.")

    module_stock_available_sale = fields.Boolean(
        string='Exclude goods already in sale quotations',
        help="This will subtract quantities from the sale quotations from "
             "the quantities available to promise.\n"
             "This installs the modules stock_available_sale.\n"
             "If the modules sale and sale_delivery_date are not "
             "installed, this will install them too")

    module_stock_available_mrp = fields.Boolean(
        string='Include the production potential',
        help="This will add the quantities of goods that can be "
             "immediately manufactured, to the quantities available to "
             "promise.\n"
             "This installs the module stock_available_mrp.\n"
             "If the module mrp is not installed, this will install it "
             "too")
