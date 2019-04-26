# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


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
        help="It must be in the same category than "
             "the default unit of measure.",
        required=False
    )
    uom_categ_domain_id = fields.Many2one(
        default=_default_uom_categ_domain_id,
        comodel_name='product.uom.categ'
    )
    qty = fields.Float(
        compute="_compute_qty",
        inverse="_inverse_qty",
        store=True,
        readonly=True
    )

    @api.multi
    @api.depends('uom_id', 'product_tmpl_id.uom_id')
    def _compute_qty(self):
        """
        Compute the quantity by package based on uom
        """
        for packaging in self:
            if packaging.uom_id and packaging.product_tmpl_id:
                packaging.qty = self.env['product.uom']._compute_qty_obj(
                    packaging.uom_id,
                    1,
                    to_unit=packaging.product_tmpl_id.uom_id)
            else:
                packaging.qty = 0

    @api.multi
    def _inverse_qty(self):
        """
        The inverse method is defined to make the code compatible with
        existing modules and to not break tests...
        :return:
        """
        for packaging in self:
            category_id = packaging.product_tmpl_id.uom_id.category_id
            uom_id = packaging.uom_id.search([
                ("factor", "=", 1.0 / self.qty),
                ('category_id', '=', category_id.id)])
            if not uom_id:
                uom_id = packaging.uom_id.create({
                    'name': "%s %s" % (category_id.name, packaging.qty),
                    'category_id': category_id.id,
                    'rounding': packaging.product_tmpl_id.uom_id.rounding,
                    'uom_type': 'bigger',
                    'factor_inv': packaging.qty,
                    'active': True
                })
            packaging.uom_id = uom_id

    @api.multi
    @api.constrains('uom_id')
    def _check_uom_id(self):
        """ Check uom_id is not null

        Since the field can be computed by the inverse method on 'qty',
        it's no more possible to add a sql constrains on the column uom_id.
        """
        for rec in self:
            if not rec.uom_id:
                raise ValidationError(_("The field Unit of Measure is "
                                        "required"))
