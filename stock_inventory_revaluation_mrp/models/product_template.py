# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_lock_cost = fields.Boolean(
        compute="_compute_allow_lock_cost", string="Allow Lock Cost Price"
    )
    standard_price = fields.Float('Cost (Active)')
    proposed_cost_ignore_bom = fields.Boolean(
        help="This product is preferably purchased, so don't use BoM when rolling up cost")

    def _compute_allow_lock_cost(self):
        for product in self:
            product.allow_lock_cost = (
                True if self.env.user.company_id.lock_cost_products else False
            )


class ProductProduct(models.Model):
    _inherit = "product.product"

    proposed_cost_ignore_bom = fields.Boolean()


    def calculate_proposed_cost(self):
        self.ensure_one()
        line_obj = self.env['mrp.bom']
        aa = []
        bo = []
        def _create_lines(bom):
            bom_ids = self.env['mrp.bom']
            bom_ids |= bom
            for line in bom.bom_line_ids:
                line_boms = line.product_id.bom_ids
                if line_boms:
                    bom_ids |= _create_lines(line_boms)
                else:
                    bom_ids |= bom
            return bom_ids


        for bom_ids in self.bom_ids:
            a = _create_lines(bom_ids)

    @api.model
    def search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
    ):
        res = super(ProductProduct, self).search(
            args, offset, limit, order, count=count
        )
        context = dict(self.env.context)
        if any(i[0] == "proposed_cost" for i in args):
            if context.get("proposed_cost_child_of"):
                product_list = self
                mrp_bom_rec = self.env['mrp.bom'].search([])
                for rec in mrp_bom_rec:
                    bom_line = self.env['mrp.bom.line'].search([('bom_id', '=', rec.id)])
                    for line in bom_line:
                        if line.bom_id.product_id.proposed_cost > 0.0:
                            product_list |= line.product_id
                            product_list |= line.bom_id.product_id
                        break
                res |= product_list
        return res
