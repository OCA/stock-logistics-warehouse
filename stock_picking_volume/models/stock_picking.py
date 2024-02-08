# Copyright 2023 ACSONE SA/NV
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
    volume_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Volume Unit of Measure",
        help="Volume Unit of Measure",
        domain=lambda self: self._get_volume_uom_domain(),
        default=lambda self: self._get_volume_uom_default(),
    )
    volume_uom_name = fields.Char(
        string="Volume unit of measure label", compute="_compute_volume_uom_name"
    )

    def _get_volume_uom_domain(self):
        domain = [("category_id", "=", self.env.ref("uom.product_uom_categ_vol").id)]
        return domain

    def _get_volume_uom_default(self):
        return self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter()

    @api.depends("move_ids", "move_ids.volume", "move_ids.state")
    def _compute_volume(self):
        default_uom = self._get_volume_uom_default()
        for picking in self:
            moves = picking.move_ids
            exclude_cancel = any(m.state != "cancel" for m in moves)
            volume = 0
            for move in moves:
                if move.state == "cancel" and exclude_cancel:
                    continue
                volume += move.volume

            volume_converted = default_uom._compute_quantity(volume, self.volume_uom_id)
            if picking.volume != volume_converted:
                picking.volume = volume_converted

    @api.onchange("volume_uom_id")
    def _onchange_volume_uom(self):
        old_uom = self._origin.volume_uom_id
        self.volume = old_uom._compute_quantity(self.volume, self.volume_uom_id)

    @api.depends("volume_uom_id")
    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.volume_uom_id.name
