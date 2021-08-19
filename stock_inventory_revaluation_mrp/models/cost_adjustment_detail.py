# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CostAdjustmentDetail(models.Model):
    _name = "cost.adjustment.detail"
    _description = "Cost Adjustment Detail"
    _order = "cost_adjustment_id"

    cost_adjustment_id = fields.Many2one(
        "cost.adjustment",
        string="Cost Adjustment",
        check_company=True,
        index=True,
        required=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        check_company=True,
        index=True,
        required=True,
    )
    product_original_cost = fields.Float(
        string="Current Cost",
        # readonly=True,
        default=0,
    )
    product_cost = fields.Float(
        string="Future Cost",
        # readonly=True,
        states={"confirm": [("readonly", False)]},
        default=0,
    )
    difference_cost = fields.Float(
        string="Difference",
        compute="_compute_difference",
        help="Indicates the gap between the product's original cost and its new cost.",
        readonly=True,
        store=True,
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
    parent_product_id = fields.Many2one("product.product", string="Parent Product")
    bom_line_id = fields.Many2one(
        "mrp.bom.line",
        string="BoM Line",
    )
    quantity = fields.Float("Quantity")
    bom_id = fields.Many2one(
        "mrp.bom",
        string="BoM",
    )
    current_bom_cost = fields.Float(
        compute="_compute_current_bom_cost", string="Current BoM Cost", store=True
    )
    future_bom_cost = fields.Float(
        compute="_compute_future_bom_cost", string="Future BoM Cost", store=True
    )
    percent_difference = fields.Float(
        compute="_compute_get_diff_percent",
        string="% Difference",
        store=True,
        group_operator="avg",
    )
    bom_product_qty_on_hand = fields.Float(
        compute="_compute_bom_product_qty_on_hand", string="On Hand Qty", store=True
    )

    @api.depends("bom_id")
    def _compute_bom_product_qty_on_hand(self):
        for line in self:
            line.bom_product_qty_on_hand = (
                line.bom_id.product_id and line.bom_id.product_id.qty_available
            ) or line.bom_id.product_tmpl_id.qty_available

    @api.depends("current_bom_cost", "future_bom_cost")
    def _compute_get_diff_percent(self):
        for line in self:
            line.percent_difference = 0.0
            if line.current_bom_cost > 0.0 and line.future_bom_cost > 0.0:
                line.percent_difference = (
                    line.difference_cost * 100
                ) / line.current_bom_cost

    @api.depends("quantity", "product_original_cost")
    def _compute_current_bom_cost(self):
        for line in self:
            line.current_bom_cost = line.quantity * line.product_original_cost

    @api.depends("quantity", "product_cost")
    def _compute_future_bom_cost(self):
        for line in self:
            line.future_bom_cost = line.quantity * line.product_cost

    @api.depends("current_bom_cost", "future_bom_cost")
    def _compute_difference(self):
        for line in self:
            line.difference_cost = line.future_bom_cost - line.current_bom_cost
