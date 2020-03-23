# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class DateRange(models.Model):
    _inherit = "date.range"

    days = fields.Integer(
        string="Days between dates", compute="_compute_days", readonly=True,
    )

    @api.multi
    @api.depends("date_start", "date_end")
    def _compute_days(self):
        for rec in self.filtered(lambda x: x.date_start and x.date_end):
            rec.days = abs((rec.date_end - rec.date_start).days) + 1
