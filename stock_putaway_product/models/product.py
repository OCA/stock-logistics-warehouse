# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_putaway_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='product_tmpl_id',
        string="Product stock locations")
    is_product_variant = fields.Boolean(compute='_compute_is_variant_product')

    @api.multi
    def _compute_is_variant_product(self):
        for product in self:
            product.is_product_variant = False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_putaway_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='product_product_id',
        string="Product stock locations")
    is_product_variant = fields.Boolean(compute='_compute_is_variant_product')

    @api.multi
    def _compute_is_variant_product(self):
        for product in self:
            product.is_product_variant = True
