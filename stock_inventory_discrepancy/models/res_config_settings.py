# Copyright 2024 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    inventory_discrepancy_enable = fields.Boolean(
        related="company_id.inventory_discrepancy_enable",
        readonly=False,
        string="Inventory Discrepancy Control",
        help="Block validation of the inventory adjustment if discrepancy exceeds "
        "the threshold.",
    )
