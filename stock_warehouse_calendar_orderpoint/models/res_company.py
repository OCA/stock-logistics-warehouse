# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    orderpoint_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Reordering Calendar",
        help="Calendar used to compute the lead date of reordering rules",
    )
    orderpoint_on_workday = fields.Boolean(
        string="Schedule the lead date on workday only",
        help="Postpone the lead date to the first available workday",
    )
