# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    reserve_area_id = fields.Many2one(
        related="location_src_id.reserve_area_id",
        help="Reserve area of the components location",
        readonly=True,
    )
