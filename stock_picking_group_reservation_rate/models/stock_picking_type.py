# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    additional_picking_type_group_id = fields.Many2one(
        comodel_name="stock.picking.type.group",
    )
