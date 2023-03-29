# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

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

    @api.depends("product_id", "product_uom_qty", "state", "move_line_ids.reserved_qty")
    def _compute_volume(self):
        for move in self:
            qty = move.product_uom_qty
            if move.state in ("partially_available", "assigned"):
                qty = move.reserved_availability
            new_volume = move._get_volume_for_qty(qty=qty)
            if move.volume != new_volume:
                move.volume = new_volume

    def _get_volume_for_qty(self, qty):
        """Return the volume for the move.

        This method is meant to be inherited to change the volume
        computation for a specific move.

        qty: float quantity to compute the volume for.

        An override of this method could take into account the packaging
        of the product to compute the volume. (using the volume information
        on the packaging provided by the module stock_quant_package_dimension
        and the method product_qty_by_packaging on the product provided by the
        module stock_packaging_calculator)
        """
        self.ensure_one()
        return qty * self.product_id.volume

    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.env[
            "product.template"
        ]._get_volume_uom_name_from_ir_config_parameter()
