# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    @api.model
    def _default_uom_categ_domain_id(self):
        uom_id = self.env.context.get("get_uom_categ_from_uom")
        if not uom_id:
            return self.env['product.uom.categ']
        uom = self.env['product.uom'].browse(uom_id)
        return uom.category_id.id

    uom_id = fields.Many2one(
        'product.uom',
        'Unit of Measure',
        required=True,
        help="It must be in the same category than "
             "the default unit of measure."
    )
    uom_categ_domain_id = fields.Many2one(
        default=_default_uom_categ_domain_id,
        comodel_name='product.uom.categ'
    )
    qty = fields.Float(
        compute="_compute_qty",
        store=True,
        readonly=True
    )

    @api.one
    @api.depends('uom_id', 'product_tmpl_id.uom_id')
    def _compute_qty(self):
        """
        Compute the quantity by package based on uom
        """
        if self.uom_id and self.product_tmpl_id:
            self.qty = self.uom_id._compute_quantity(
                1, to_unit=self.product_tmpl_id.uom_id)
        else:
            self.qty = 0
