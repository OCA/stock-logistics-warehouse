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
        cost = self.proposed_cost or self.standard_price
        return cost

    def calculate_proposed_cost(self):
        DecimalPrecision = self.env["decimal.precision"]
        computed_products = {}
        products = self.filtered(
            lambda x: (x.bom_ids or x.is_cost_type) and not x.proposed_cost_ignore_bom
        )
        for product in products:
            # cost type services
            if product.is_cost_type:
                total = total_uom = 0
                for act_cost_rule in product.activity_cost_ids:
                    linetotal = act_cost_rule.product_id._get_rollup_cost()
                    total_uom += linetotal * act_cost_rule.factor
            # products
            else:
                bom = self.env["mrp.bom"]._bom_find(product)[product]
                # First recompute "Proposed Cost" for the BoM components that also have a BoM
                components = bom.bom_line_ids.product_id
                components = components.filtered(
                    lambda pr: pr.id not in [*computed_products]
                )
                intermediates = components.calculate_proposed_cost()
                computed_products.update(intermediates)

                # Add the costs for all Components and Operations,
                # using the Active Cost when available, or the Proposed Cost otherwise
                cost_components = sum(
                    x.product_id.uom_id._compute_price(
                        x.product_id._get_rollup_cost(), x.product_uom_id
                    )
                    * x.product_qty
                    for x in bom.bom_line_ids
                )
                op_products = bom.operation_ids.mapped("workcenter_id").mapped(
                    "analytic_product_id"
                )
                op_products = op_products.filtered(
                    lambda pr: pr.id not in [*computed_products]
                )
                op_cost_types = op_products.calculate_proposed_cost()
                computed_products.update(op_cost_types)

                cost_operations = sum(
                    x.workcenter_id.analytic_product_id._get_rollup_cost()
                    * (x.time_cycle / 60)
                    for x in bom.operation_ids
                )
                total = cost_components + cost_operations
                total_uom = bom.product_uom_id._compute_price(
                    total / bom.product_qty, product.uom_id
                )

            # Set proposed cost if different from the actual cost
            has_proposed_cost = False
            if product.standard_price != total_uom:
                has_proposed_cost = True
            product.proposed_cost = total_uom if has_proposed_cost else 0.0
            computed_products[product.id] = 1

        return computed_products

    def _get_bom_structure_products(self):
        BOM = self.env["mrp.bom"]
        assemblies = self.filtered(
            lambda x: x.bom_ids and not x.proposed_cost_ignore_bom
        )
        bom_structure = assemblies
        for product in assemblies:
            bom = BOM._bom_find(product)[product]
            product_bom = bom.get(product)
            components = product_bom.bom_line_ids.product_id
            bom_structure |= components._get_bom_structure_products()
        return bom_structure

    def update_bom_version(self):
        bom_line_obj = self.env["mrp.bom.line"]
        bom_obj = self.env["mrp.bom"]
        no_of_bom_version = self.env.company.no_of_bom_version
        adjustment_obj = self.env["stock.cost.adjustment.detail"]
        adjustment_id = self._context.get("adjustment_id")
        for product in self:
            bom_ids = adjustment_obj.search(
                [
                    ("parent_product_id", "=", product.id),
                    ("cost_adjustment_line_id.cost_adjustment_id", "=", adjustment_id),
                ]
            ).mapped('bom_id')
            for bom_id in bom_ids:
                active_bom = bom_obj.search(
                    [
                        ("product_id", "=", bom_id.product_id.id),
                        ("active", "=", False),
                        ("cost_roll_up_version", "!=", False)
                        # ("active_ref_bom", "=", True),
                    ],
                    order="id DESC",
                )
                active_bom.write({"active_ref_bom": False})
                if active_bom and len(active_bom) >= no_of_bom_version:
                    limit = (len(active_bom) - no_of_bom_version) + 1
                    unlink_bom = bom_obj.search(
                        [
                            ("product_id", "=", bom_id.product_id.id),
                            ("active", "=", False),
                            ("active_ref_bom", "=", False),
                            ("cost_roll_up_version", "!=", False),
                        ],
                        order="id asc",
                        limit=limit,
                    )
                    unlink_bom.unlink()
                new_bom = bom_id.copy(
                    {
                        "active": False,
                        "active_ref_bom": True,
                        "cost_roll_up_version": True,
                    }
                )
                line_ids = new_bom.bom_line_ids.filtered(
                    lambda l: l.product_id.id == product.id
                )
                line_ids.write({"unit_cost": product.standard_price})
                for operatine in new_bom.operation_ids.filtered(
                    lambda l: l.workcenter_id.analytic_product_id.activity_cost_ids
                ):
                    activity_cost_ids = []
                    for (
                        activity
                    ) in operatine.workcenter_id.analytic_product_id.activity_cost_ids:
                        activity_cost_ids.append(
                            (
                                0,
                                0,
                                {
                                    "analytic_product_id": operatine.workcenter_id.analytic_product_id.id,
                                    "product_id": activity.product_id.id,
                                    "standard_price": activity.standard_price,
                                    "factor": activity.factor,
                                },
                            )
                        )
                    if activity_cost_ids:
                        operatine.write({"operation_info_ids": activity_cost_ids})
