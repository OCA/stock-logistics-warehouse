# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_lock_cost = fields.Boolean(
        compute="_compute_allow_lock_cost", string="Allow Lock Cost Price"
    )
    standard_price = fields.Float("Cost (Active)")
    proposed_cost_ignore_bom = fields.Boolean(
        help="This product is preferably purchased, so don't use BoM when rolling up cost"
    )

    def _compute_allow_lock_cost(self):
        for product in self:
            product.allow_lock_cost = (
                True if self.env.user.company_id.lock_cost_products else False
            )


class ProductProduct(models.Model):
    _inherit = "product.product"

    proposed_cost_ignore_bom = fields.Boolean()

    def _get_rollup_cost(self):
        cost = self.standard_price or self.proposed_cost
        return cost

    def calculate_proposed_cost(self):
        products = self.filtered(lambda x: x.bom_ids and not x.proposed_cost_ignore_bom)
        for product in products:
            bom = product.bom_ids[:1]
            # First recompute "Proposed Cost" for the BoM components that also have a BoM
            bom.bom_line_ids.product_id.calculate_proposed_cost()
            # Add the costs for all Components and Operations,
            # using the Active Cost when available, or the Proposed Cost otherwise
            cost_components = sum(
                x.product_id.uom_id._compute_price(
                    x.product_id._get_rollup_cost(), x.product_uom_id
                )
                * x.product_qty
                for x in bom.bom_line_ids
            )
            cost_operations = sum(
                x.workcenter_id._get_rollup_cost() * (x.time_cycle / 60)
                for x in bom.operation_ids
            )
            total = cost_components + cost_operations
            total_uom = bom.product_uom_id._compute_price(
                total / bom.product_qty, product.uom_id
            )
            # TODO: only set Propsoed Cost if different from actual cost!
            product.proposed_cost = total_uom

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
        if any(i[0] == "proposed_cost" for i in args):
            if self.env.context.get("proposed_cost_child_of"):
                product_list = self
                mrp_bom_rec = self.env["mrp.bom"].search([])  # FIXME: too greedy!
                for rec in mrp_bom_rec:
                    bom_line = self.env["mrp.bom.line"].search(
                        [("bom_id", "=", rec.id)]
                    )
                    for line in bom_line:
                        if line.bom_id.product_id.proposed_cost > 0.0:
                            product_list |= line.product_id
                            product_list |= line.bom_id.product_id
                        break
                res |= product_list
        return res
