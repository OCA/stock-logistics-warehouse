# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.tools.float_utils import float_compare


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
            product.allow_lock_cost = self.env.user.company_id.lock_cost_products


class ProductProduct(models.Model):
    _inherit = "product.product"

    proposed_cost_ignore_bom = fields.Boolean()

    def _get_rollup_cost(self):
        cost = self.standard_price or self.proposed_cost
        return cost

    def calculate_proposed_cost(self):
        DecimalPrecision = self.env["decimal.precision"]
        products = self.filtered(lambda x: x.bom_ids and not x.proposed_cost_ignore_bom)
        for product in products:
            bom = self.env["mrp.bom"]._bom_find(product=product)
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
            # Set proposed cost if different from the actual cost
            rounding = DecimalPrecision.precision_get("Product Price")
            has_proposed_cost = float_compare(
                product.standard_price, total_uom, precision_rounding=rounding
            )
            product.proposed_cost = total_uom if has_proposed_cost else 0.0

    def _get_bom_structure_products(self):
        BOM = self.env["mrp.bom"]
        assemblies = self.filtered(
            lambda x: x.bom_ids and not x.proposed_cost_ignore_bom
        )
        bom_structure = assemblies
        for product in assemblies:
            bom = BOM._bom_find(products=product)
            product_bom = bom.get(product)
            components = product_bom.bom_line_ids.product_id
            bom_structure |= components._get_bom_structure_products()
        return bom_structure
