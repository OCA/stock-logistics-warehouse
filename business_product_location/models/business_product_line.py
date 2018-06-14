# -*- coding: utf-8 -*-
# Copyright 2015-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class BusinessProductLine(models.Model):

    _name = 'business.product.line'
    _rec_name = "product_id"

    @api.model
    def _default_product_uom_id(self):
        return self.env.ref('product.product_uom_unit')

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    product_qty = fields.Float(
        'Product Quantity',
        required=True,
        digits=dp.get_precision('Product Unit of Measure')
    )
    product_uom_id = fields.Many2one(
        'product.uom',
        'Product Unit of Measure',
        required=True,
        default=_default_product_uom_id
    )
    business_product_location_id = fields.Many2one(
        'business.product.location',
        'Parent business product location',
        required=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ Change UoM if product_id changes
        """
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id

    @api.onchange('product_uom_id')
    def _onchange_product_uom_id(self):
        """ Check the selected UoM with the product UoM
        """
        res = {}
        if self.product_id and self.product_uom_id:
            if self.product_id.uom_id.category_id.id != \
                    self.product_uom_id.category_id.id:
                res['warning'] = {
                    'title': _('Warning'),
                    'message': _('The Product Unit of Measure you chose '
                                 'has a different category than in the '
                                 'product form.')}
                self.product_uom_id = self.product_id.uom_id
        return res
