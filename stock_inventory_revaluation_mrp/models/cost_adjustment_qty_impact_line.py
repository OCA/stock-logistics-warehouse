# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CostAdjustmentImpactLine(models.Model):
    _name = "cost.adjustment.qty.impact.line"
    _description = "Cost Adjustment Impact Line"

    cost_adjustment_id = fields.Many2one(
        "cost.adjustment",
        string="Cost Adjustment",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        index=True,
        required=True,
    )
    product_original_cost = fields.Float(
        string="Current Cost",
        readonly=True,
        default=0,
        copy=False,
    )
    product_cost = fields.Float(
        string="Future Cost",
        readonly=True,
        default=0,
        copy=False,
    )
    difference_cost = fields.Float(
        string="Difference",
        compute="_compute_difference",
        readonly=True,
        store=True,
    )
    percent_difference = fields.Float(
        compute="_compute_diff_in_percent", string="% Difference"
    )
    qty_on_hand = fields.Float(string="QTY On Hand", readonly=True)
    total_difference = fields.Float(
        string="Impact",
        compute="_compute_difference",
        store=True,
    )
    bom_id = fields.Many2one(
        "mrp.bom",
        string="BoM",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="cost_adjustment_id.company_id",
        index=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="company_id.currency_id",
    )

    @api.depends("product_original_cost", "product_cost", "difference_cost")
    def _compute_diff_in_percent(self):
        for line in self:
            line.percent_difference = 0.0
            if line.product_cost > 0.0 and line.product_original_cost > 0.0:
                line.percent_difference = (
                    line.difference_cost * 100 / line.product_original_cost
                )

    @api.depends("product_cost", "product_original_cost", "qty_on_hand")
    def _compute_difference(self):
        for line in self:
            cost_diff = line.product_cost - line.product_original_cost
            line.difference_cost = cost_diff
            line.total_difference = cost_diff * line.qty_on_hand
