# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_qty_reason_preset = fields.Boolean(
        string="Preset Change Qty Reason",
        required=True,
        implied_group="stock_change_qty_reason.group_qty_reason_preset",
        help="Enable use of predefined Reasons to manage Inventory Adjustments"
        "and Product Update Quantities Wizard.",
    )
