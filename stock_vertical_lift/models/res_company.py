# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    vertical_lift_pick_by_priority = fields.Boolean(
        string="Pick urgent transfers first",
        default=True,
        help="Propose the move lines of the most urgent transfers first, "
        "using the transfer's priority and scheduled date.",
    )
    vertical_lift_pick_skipped_last = fields.Boolean(
        string="Pick skipped lines last",
        default=True,
        help="Move lines skipped by the operator are proposed again only once "
        "the other move lines have been processed.",
    )
