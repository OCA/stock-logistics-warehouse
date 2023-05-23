# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.picking"

    reserve_area_line_ids = fields.One2many(
        "stock.move.reserve.area.line",
        "picking_id",
        help="Reserve areas of the source location",
    )
