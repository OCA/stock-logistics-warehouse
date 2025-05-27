# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_soft_inventory_lock = fields.Boolean(
        related="company_id.use_soft_inventory_lock", readonly=False
    )
