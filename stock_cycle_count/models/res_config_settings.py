# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_start_inventory_from_cycle_count = fields.Boolean(
        related="company_id.auto_start_inventory_from_cycle_count",
        string="Auto Start Inventory Adjustment from Cycle Count",
        help="If enabled, confirming a Cycle Count will start the "
        "related Inventory Adjustment.",
        readonly=False,
    )

    inventory_adjustment_counted_quantities = fields.Selection(
        related="company_id.inventory_adjustment_counted_quantities",
        string="Inventory Adjustment Counted quantities from Cycle Count",
        help="If enabled, confirming a Cycle Count will start the related "
        "Inventory Adjustment.",
        readonly=False,
    )
