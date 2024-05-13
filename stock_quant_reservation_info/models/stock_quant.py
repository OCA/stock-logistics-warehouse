# Copyright 2022 ForgeFlow <http://www.forgeflow.com>

from odoo import _, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def action_reserved_moves(self):
        self.ensure_one()
        action = {
            "name": _(
                "Reserved Moves for: %(product_name)s",
                product_name=self.product_id.name,
            ),
            "view_mode": "list,form",
            "res_model": "stock.move.line",
            "views": [
                (
                    self.env.ref(
                        "stock_quant_reservation_info.view_stock_move_line_reserved_info_tree"
                    ).id,
                    "list",
                ),
                (False, "form"),
            ],
            "type": "ir.actions.act_window",
            "context": {},
            "domain": [
                ("product_id", "=", self.product_id.id),
                ("product_uom_qty", ">", 0),
                ("location_id.usage", "=", "internal"),
                ("lot_id", "=", self.lot_id.id),
                ("owner_id", "=", self.owner_id.id),
            ],
        }
        return action
