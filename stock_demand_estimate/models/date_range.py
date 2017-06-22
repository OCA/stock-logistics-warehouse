# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DateRange(models.Model):
    _inherit = "date.range"

    @api.multi
    @api.depends('date_start', 'date_end')
    def _compute_days(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                rec.days = abs((fields.Date.from_string(
                    rec.date_end) - fields.Date.from_string(
                    rec.date_start)).days) + 1

    days = fields.Float(string="Days between dates",
                        compute='_compute_days', readonly=True)
