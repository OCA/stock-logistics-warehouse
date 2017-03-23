# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _get_domain_locations(self):
        param_obj = self.env['ir.config_parameter']
        expired_lots = param_obj.get_param(
            'stock_qty_available_lot_expired',
            False)
        if not expired_lots:
            return super(ProductProduct, self)._get_domain_locations()

        quant_domain, move_in_domain, move_out_domain = super(
            ProductProduct, self)._get_domain_locations()

        pivot_date = self.env.context.get('pivot_date', False)
        if not pivot_date:
            pivot_date = fields.Datetime.now()

        quant_domain += [
            '|',
            ('lot_id', '=', False),
            '&',
            '&',
            ('lot_id', '!=', False),
            ('lot_id.removal_date', '!=', False),
            ('lot_id.removal_date', '>', pivot_date)]

        return quant_domain, move_in_domain, move_out_domain
