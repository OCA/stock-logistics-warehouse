# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingTypeGroup(models.Model):
    _name = "stock.picking.type.group"
    _description = "Stock Picking Type Group"

    name = fields.Char(translate=True)
    active = fields.Boolean(default=True)
    picking_type_ids = fields.One2many(
        comodel_name="stock.picking.type",
        inverse_name="picking_type_group_id",
        string="Operation Types",
    )
