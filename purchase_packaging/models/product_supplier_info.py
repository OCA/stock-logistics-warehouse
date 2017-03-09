# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def _default_min_qty_uom_id(self):
        return self.env.ref('product.product_uom_unit')

    packaging_id = fields.Many2one(
        'product.packaging',
        'Logisitical Units'
    )
    product_uom = fields.Many2one(
        compute='_compute_product_uom',
        string="Supplier Unit of Measure",
        related=False
    )
    min_qty_uom_id = fields.Many2one(
        'product.uom',
        'Minimal Unit of Measure Quantity',
        required=True,
        default=_default_min_qty_uom_id
    )

    @api.multi
    @api.depends('product_tmpl_id', 'packaging_id')
    def _compute_product_uom(self):
        """ Set product_uom as a computed field instead of a related field.
            To use uom of link packaging
        """
        for rec in self:
            rec.product_uom = rec.packaging_id.uom_id or \
                rec.product_id.uom_po_id or \
                rec.product_tmpl_id.uom_po_id
