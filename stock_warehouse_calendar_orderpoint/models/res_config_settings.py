# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    orderpoint_calendar_id = fields.Many2one(
        related="company_id.orderpoint_calendar_id",
        readonly=False,
    )
    orderpoint_on_workday_policy = fields.Selection(
        related="company_id.orderpoint_on_workday_policy",
        readonly=False,
    )
