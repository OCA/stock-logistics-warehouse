# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CostAdjustmentLine(models.Model):
    _name = "stock.cost.adjustment.line"
    _description = "Cost Adjustment Line"
    _order = "product_id, cost_adjustment_id"

    is_editable = fields.Boolean(
        string="Editable?", help="Technical field to restrict editing."
    )
    cost_adjustment_id = fields.Many2one(
        "stock.cost.adjustment",
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
    product_type = fields.Selection(
        string="Product Type", related="product_id.type", readonly=True
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
        states={"confirm": [("readonly", False)]},
        default=0,
        copy=False,
    )
    difference_cost = fields.Float(
        string="Difference",
        compute="_compute_difference",
        help="Indicates the gap between the product's original cost and its new cost.",
        readonly=True,
        store=True,
    )
    categ_id = fields.Many2one(related="product_id.categ_id", store=True)
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
    state = fields.Selection(related="cost_adjustment_id.state")
    cost_adjustment_date = fields.Datetime(
        string="Cost Adjustment Date",
        related="cost_adjustment_id.date",
        help="Last date at which the On Hand Quantity has been computed.",
    )
    qty_on_hand = fields.Float(string="QTY On Hand", readonly=True)
    total_difference = fields.Float(
        string="Impact",
        compute="_compute_difference",
        store=True,
    )
    price_outdated = fields.Boolean(
        string="Price Outdated", compute="_compute_outdated"
    )
    qty_outdated = fields.Boolean(string="Qty Outdated", compute="_compute_outdated")
    percent_difference = fields.Float(
        compute="_compute_diff_in_percent", string="% Difference"
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

    @api.depends(
        "product_original_cost", "product_id.standard_price", "product_id.quantity_svl"
    )
    def _compute_outdated(self):
        for line in self:
            line.price_outdated = (
                line.product_original_cost != line.product_id.standard_price
            )
            line.qty_outdated = line.product_id.qty_available != line.qty_on_hand

    @api.onchange("product_id")
    def _set_costs(self):
        for line in self:
            if line.state not in ("posted"):
                self.write(
                    {
                        "product_cost": (
                            self.product_id.proposed_cost
                            if self.product_id.proposed_cost > 0.0
                            else self.product_id.standard_price
                        ),
                        "product_original_cost": self.product_id.standard_price,
                        "qty_on_hand": line.product_id.qty_available,
                    }
                )

    def action_refresh_quantity(self):
        filtered_lines = self.filtered(lambda l: l.state != "posted")
        for line in filtered_lines:
            if line.qty_on_hand != line.product_id.qty_available:
                line.qty_on_hand = line.product_id.qty_available

    def action_get_origin_cost(self):
        filtered_lines = self.filtered(lambda l: l.state != "posted")
        for line in filtered_lines:
            origin_cost = line.product_id.standard_price
            if line.product_original_cost != origin_cost:
                line.product_original_cost = origin_cost

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.action_refresh_quantity()
        return res

    @api.constrains("product_id", "cost_adjustment_id")
    def _check_no_duplicate_line(self):
        for line in self:
            domain = [
                ("id", "!=", line.id),
                ("product_id", "=", line.product_id.id),
                ("cost_adjustment_id", "=", line.cost_adjustment_id.id),
            ]
            existings = self.search_count(domain)
            if existings:
                raise UserError(
                    _(
                        "There is already one cost adjustment line for product %s, "
                        "you should rather modify this one instead of creating a "
                        "new one."
                    )
                    % line.product_id.display_name
                )
