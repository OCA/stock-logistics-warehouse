# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CostAdjustmentDetail(models.Model):
    _name = "stock.cost.adjustment.detail"
    _description = "Cost Adjustment Detail"

    cost_adjustment_line_id = fields.Many2one(
        "stock.cost.adjustment.line",
        index=True,
        required=True,
    )
    cost_adjustment_id = fields.Many2one(
        "stock.cost.adjustment", related="cost_adjustment_line_id.cost_adjustment_id"
    )
    product_id = fields.Many2one(
        "product.product",
        string="Impacted Product",
        check_company=True,
        index=True,
        required=True,
    )
    product_original_cost = fields.Float(
        string="Current Cost",
        related="product_id.standard_price",
    )
    cost_increase = fields.Float(
        readonly=True,
        help="Indicates cost to add to the product's original cost.",
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
        string="From Impacted BoM",
    )
    current_bom_cost = fields.Float(
        compute="_compute_current_bom_cost", string="Current BoM Cost", store=True
    )
    future_bom_cost = fields.Float(
        compute="_compute_future_bom_cost", string="Future BoM Cost", store=True
    )
    percent_difference = fields.Float(
        compute="_compute_percent_difference",
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

    @api.depends("current_bom_cost", "cost_increase")
    def _compute_percent_difference(self):
        for line in self:
            line.percent_difference = 0.0
            if line.current_bom_cost > 0.0:
                line.percent_difference = (
                    line.cost_increase * 100 / line.current_bom_cost
                )

    @api.depends("quantity", "product_original_cost")
    def _compute_current_bom_cost(self):
        for line in self:
            line.current_bom_cost = line.quantity * line.product_original_cost
