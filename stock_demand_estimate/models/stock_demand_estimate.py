# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockDemandEstimate(models.Model):
    _name = "stock.demand.estimate"
    _description = "Stock Demand Estimate Line"

    active = fields.Boolean(default=True)
    date_from = fields.Date(
        compute="_compute_dates", string="From (computed)", store=True
    )
    date_to = fields.Date(compute="_compute_dates", string="To (computed)", store=True)
    manual_date_from = fields.Date(string="From")
    manual_date_to = fields.Date(string="To")
    manual_duration = fields.Integer(
        string="Duration", help="Duration (in days)", default=1
    )
    duration = fields.Integer(
        compute="_compute_dates", string="Duration (computed))", store=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    product_uom = fields.Many2one(comodel_name="uom.uom", string="Unit of measure")
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location", required=True
    )
    product_uom_qty = fields.Float(string="Quantity", digits="Product Unit of Measure")
    product_qty = fields.Float(
        string="Quantity (Product UoM)",
        compute="_compute_product_quantity",
        inverse="_inverse_product_quantity",
        digits=0,
        store=True,
        help="Quantity in the default UoM of the product",
        readonly=True,
    )
    daily_qty = fields.Float(string="Quantity / Day", compute="_compute_daily_qty")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    @api.depends("manual_duration", "manual_date_from", "manual_date_to")
    def _compute_dates(self):
        today = date.today()
        for rec in self:
            rec.date_from = rec.manual_date_from or today
            if rec.manual_date_to:
                rec.date_to = rec.manual_date_to
                rec.duration = (rec.manual_date_to - rec.date_from).days + 1
            elif rec.manual_duration:
                rec.date_to = rec.date_from + timedelta(days=rec.manual_duration - 1)
                rec.duration = rec.manual_duration
            else:
                rec.date_to = rec.date_from + timedelta(days=1)
                rec.duration = 2

    @api.depends("product_qty", "duration")
    def _compute_daily_qty(self):
        for rec in self:
            if rec.duration:
                rec.daily_qty = rec.product_qty / rec.duration
            else:
                rec.daily_qty = 0.0

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_product_quantity(self):
        for rec in self:
            if rec.product_uom:
                rec.product_qty = rec.product_uom._compute_quantity(
                    rec.product_uom_qty, rec.product_id.uom_id
                )
            else:
                rec.product_qty = rec.product_uom_qty

    def _inverse_product_quantity(self):
        raise UserError(
            _(
                "The requested operation cannot be "
                "processed because of a programming error "
                "setting the `product_qty` field instead "
                "of the `product_uom_qty`."
            )
        )

    @api.depends("date_from", "date_to", "product_id.name", "location_id.name")
    def _compute_display_name(self):
        for rec in self:
            name = (
                f"{rec.date_from} - {rec.date_to}: {rec.product_id.name}"
                f" - {rec.location_id.name}"
            )
            rec.display_name = name

    @api.onchange("manual_date_to")
    def _onchange_manual_date_to(self):
        for rec in self:
            if rec.manual_date_from:
                rec.manual_duration = (
                    rec.manual_date_to - rec.manual_date_from
                ).days + 1

    @api.onchange("manual_duration")
    def _onchange_manual_duration(self):
        for rec in self:
            if rec.manual_date_from:
                rec.manual_date_to = rec.manual_date_from + timedelta(
                    days=rec.manual_duration - 1
                )

    @api.model
    def get_quantity_by_date_range(self, date_start, date_end):
        """To be used in other modules"""
        # Check if the dates overlap with the period
        period_date_start = self.date_from
        period_date_end = self.date_to

        # We need only the periods that overlap
        # the dates introduced by the user.
        if period_date_start <= date_end and period_date_end >= date_start:
            overlap_date_start = max(period_date_start, date_start)
            overlap_date_end = min(period_date_end, date_end)
            days = (abs(overlap_date_end - overlap_date_start)).days + 1
            return days * self.daily_qty
        return 0.0
