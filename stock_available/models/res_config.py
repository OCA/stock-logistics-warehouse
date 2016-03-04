# -*- coding: utf-8 -*-
# © 2014 Numérigraphe, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields
from openerp.tools.safe_eval import safe_eval


class StockConfig(models.TransientModel):

    """Add options to easily install the submodules"""
    _inherit = 'stock.config.settings'

    @api.model
    def _get_stock_available_mrp_based_on(self):
        """Gets the available languages for the selection."""
        fields = self.env['ir.model.fields'].search(
            [('model', '=', 'product.product'),
             ('ttype', '=', 'float')])
        return [(field.name, field.field_description) for field in fields]

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

    module_stock_available_mrp = fields.Boolean(
        string='Include the production potential',
        help="This will add the quantities of goods that can be "
             "immediately manufactured, to the quantities available to "
             "promise.\n"
             "This installs the module stock_available_mrp.\n"
             "If the module mrp is not installed, this will install it "
             "too")

    stock_available_mrp_based_on = fields.Selection(
        _get_stock_available_mrp_based_on,
        string='based on',
        help="Choose the field of the product which will be used to compute "
             "potential.\nIf empty, Quantity On Hand is used.",
    )

    @api.model
    def get_default_stock_available_mrp_based_on(self, fields):
        res = {}
        icp = self.env['ir.config_parameter']
        res['stock_available_mrp_based_on'] = safe_eval(
            icp.get_param('stock_available_mrp_based_on', 'False'))
        if not res['stock_available_mrp_based_on']:
            res['stock_available_mrp_based_on'] = 'qty_available'
        return res

    @api.multi
    def set_stock_available_mrp_based_on(self):
        if self.stock_available_mrp_based_on:
            icp = self.env['ir.config_parameter']
            icp.set_param('stock_available_mrp_based_on',
                          repr(self.stock_available_mrp_based_on))
