# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_packaging')
    def _onchange_product_packaging(self):
        """
        Set product_uom when set product_packaging
        """
        if self.product_packaging:
            self.product_uom = self.product_packaging.uom_id
            self.product_uom_change()
        return super(SaleOrderLine, self)._onchange_product_packaging()

    @api.model
    def update_vals(self, vals):
        """
        When product_packaging is set, product_uom is readonly,
        so we need to reset the uom value in the vals dict
        """
        if vals.get('product_packaging'):
            vals['product_uom'] = self.env['product.packaging'].browse(
                vals['product_packaging']).uom_id.id
        return vals

    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, vals):
        return super(SaleOrderLine, self).create(self.update_vals(vals))

    @api.multi
    def write(self, vals):
        return super(SaleOrderLine, self).write(self.update_vals(vals))
