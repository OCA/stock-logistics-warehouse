# Copyright (C) 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StocklocationContentCheckLine(models.Model):
    _name = "stock.location.content.check.line"
    _description = "Stock Location Content Check Lines"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", string="Product")
    check_id = fields.Many2one("stock.location.content.check", string="Check")
    expected_qty = fields.Float(
        compute="_compute_quantities", string="Expected Quantity"
    )
    current_qty = fields.Float(
        compute="_compute_quantities",
        string="Current Quantity",
    )
    counted_qty = fields.Float(string="Counted Quantity")
    replenished_qty = fields.Float(string="Replenished Quantity")

    @api.depends("product_id", "check_id")
    def _compute_quantities(self):
        for rec in self:
            rec.expected_qty = (
                rec.check_id
                and rec.check_id.location_id
                and rec.check_id.location_id.template_id
                and rec.check_id.location_id.template_id.line_ids.filtered(
                    lambda line: line.product_id == rec.product_id
                ).quantity
            )
            quants = self.env["stock.quant"].search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("location_id", "=", rec.check_id.location_id.id),
                ]
            )
            rec.current_qty = sum(quant.available_quantity for quant in quants)

    @api.onchange("expected_qty", "counted_qty")
    def _onchange_replenished_qty(self):
        for rec in self:
            rec.replenished_qty = rec.expected_qty - rec.counted_qty

    @api.constrains("expected_qty", "counted_qty", "replenished_qty")
    def _check_quantities(self):
        for rec in self:
            if rec.counted_qty + rec.replenished_qty > rec.expected_qty:
                raise UserError(
                    _(
                        "You cannot replenish more than expected (%s)."
                        % rec.product_id.name
                    )
                )
