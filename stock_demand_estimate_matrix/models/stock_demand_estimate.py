# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockDemandEstimate(models.Model):
    _inherit = "stock.demand.estimate"

    date_range_id = fields.Many2one(
        comodel_name="date.range", string="Estimating Period", ondelete="restrict"
    )

    @api.depends(
        "date_range_id",
        "manual_duration",
        "manual_date_from",
        "manual_date_to",
    )
    def _compute_dates(self):
        date_range_records = self.filtered(lambda r: r.date_range_id)
        res = super(StockDemandEstimate, self - date_range_records)._compute_dates()
        for rec in date_range_records:
            rec.date_from = rec.date_range_id.date_start
            rec.date_to = rec.date_range_id.date_end
            rec.duration = rec.date_range_id.days
        return res

    @api.depends("date_range_id.name")
    def _compute_display_name(self):
        date_range_records = self.filtered(lambda r: r.date_range_id)
        res = super(
            StockDemandEstimate, self - date_range_records
        )._compute_display_name()
        for rec in date_range_records:
            name = (
                f"{rec.date_range_id.name} - "
                f"{rec.product_id.name} - "
                f"{rec.location_id.name}"
            )
            rec.display_name = name
        return res
