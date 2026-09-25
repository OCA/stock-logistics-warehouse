# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    move_location_allow_immediate_transfer = fields.Boolean(
        string="Allow Immediate Transfer from Move Location Wizard",
        default=True,
        help="If disabled, the 'Immediate Transfer' button is hidden in the "
        "Move from location wizard, and only planned transfers can be created.",
    )
