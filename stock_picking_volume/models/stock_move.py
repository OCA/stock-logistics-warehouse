# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    volume = fields.Float(
        compute="_compute_volume",
        store=True,
        compute_sudo=True,
    )

    volume_uom_name = fields.Char(
        string="Volume unit of measure label", compute="_compute_volume_uom_name"
    )

    @api.depends("product_id", "product_uom_qty", "state", "quantity")
    def _compute_volume(self):
        for move in self:
            qty = move.product_uom_qty
            if move.state in ("partially_available", "assigned"):
                qty = move.quantity
            new_volume = move.product_id._get_volume_for_qty(qty, move.product_uom)
            if move.volume != new_volume:
                move.volume = new_volume

    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.env[
            "product.template"
        ]._get_volume_uom_name_from_ir_config_parameter()
