# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    """Add options to easily install the submodules"""
    _inherit = 'res.config.settings'

    @api.model
    def _get_stock_available_mrp_based_on(self):
        """Gets the available languages for the selection."""
        pdct_fields = self.env['ir.model.fields'].search(
            [('model', '=', 'product.product'),
             ('ttype', '=', 'float')])
        return [
            (field.name, field.field_description)
            for field in sorted(pdct_fields, key=lambda f: f.field_description)
        ]

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

    stock_available_mrp_based_on = fields.Selection(
        _get_stock_available_mrp_based_on,
        string='based on',
        help="Choose the field of the product which will be used to compute "
             "potential.\nIf empty, Quantity On Hand is used.\n"
             "Only the quantity fields have meaning for computing stock",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(stock_available_mrp_based_on=self.env[
            'ir.config_parameter'].sudo().get_param(
                'stock_available_mrp_based_on',
                'qty_available')
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'stock_available_mrp_based_on', self.stock_available_mrp_based_on)
