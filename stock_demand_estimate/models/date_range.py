# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import ValidationError


class DateRange(models.Model):
    _inherit = "date.range"

    @api.multi
    @api.depends('date_start', 'date_end')
    def _compute_days(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                rec.days = (fields.Date.from_string(rec.date_start) -
                            fields.Date.from_string(rec.date_end)).days + 1

    days = fields.Float(string="Days between dates",
                        compute='_compute_days', store=True, readonly=True)
