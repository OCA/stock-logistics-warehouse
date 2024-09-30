# Copyright 2023 ACSONE SA/NV
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    volume = fields.Float(
        compute="_compute_volume",
        readonly=False,
        store=True,
        compute_sudo=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )
    volume_uom_name = fields.Char(
        string="Volume unit of measure label", compute="_compute_volume_uom_name"
    )

    @api.depends("move_lines", "move_lines.volume", "move_lines.state")
    def _compute_volume(self):
        for picking in self:
            moves = picking.move_lines
            exclude_cancel = any(m.state != "cancel" for m in moves)
            volume = 0
            for move in moves:
                if move.state == "cancel" and exclude_cancel:
                    continue
                volume += move.volume
            if picking.volume != volume:
                picking.volume = volume

    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.env[
            "product.template"
        ]._get_volume_uom_name_from_ir_config_parameter()
