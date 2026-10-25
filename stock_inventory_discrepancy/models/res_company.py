# Copyright 2024 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    inventory_discrepancy_enable = fields.Boolean(
        string="Inventory Discrepancy Control",
        help="Block validation of the inventory adjustment if discrepancy exceeds "
        "the threshold.",
    )
