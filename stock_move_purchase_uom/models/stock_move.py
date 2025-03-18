# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves:
            purchase_uom = move.product_id.uom_po_id
            if (
                move.product_id
                and move.picking_type_id
                and move.picking_type_id.use_purchase_uom
                and purchase_uom
                and move.product_uom != purchase_uom
                and not move.origin_returned_move_id
            ):
                updated_product_uom_qty = move.product_uom._compute_quantity(
                    move.product_uom_qty,
                    purchase_uom,
                    rounding_method=move.picking_type_id.purchase_uom_rounding_method,
                )
                move.product_uom = move.product_id.uom_po_id
                move.product_uom_qty = updated_product_uom_qty
        return moves

    @api.onchange("product_id", "picking_type_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if self.product_id:
            if self.picking_type_id and self.picking_type_id.use_purchase_uom:
                self.product_uom = self.product_id.with_context(
                    lang=self._get_lang()
                ).uom_po_id.id
        return res
