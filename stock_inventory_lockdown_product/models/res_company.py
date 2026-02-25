# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    use_soft_inventory_lock = fields.Boolean(
        string="Use Product-Aware Inventory Lock",
        help="When enabled, only restrict stock moves if "
        "the product is part of an ongoing inventory adjustment at the location.",
    )
