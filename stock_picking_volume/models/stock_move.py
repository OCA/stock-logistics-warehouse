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

    def _get_processible_quantity(self):
        if self.state in ("partially_available", "assigned"):
            return self.quantity
        return self.product_uom_qty

    @api.depends("product_id", "product_uom_qty", "state", "quantity")
    def _compute_volume(self):
        for move in self:
            product = move.product_id
            if product and product.type == "consu":
                quantity = move._get_processible_quantity()
                volume = product._get_volume_for_qty(quantity, move.product_uom)
            else:
                volume = 0
            if move.volume != volume:
                move.volume = volume

    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.env[
            "product.template"
        ]._get_volume_uom_name_from_ir_config_parameter()
