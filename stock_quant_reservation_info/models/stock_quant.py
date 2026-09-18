# Copyright 2022 ForgeFlow <http://www.forgeflow.com>

from odoo import models
from odoo.fields import Domain


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def action_reserved_moves(self):
        self.ensure_one()
        action = {
            "name": self.env._(
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
            "domain": Domain.AND(
                [
                    Domain("product_id", "=", self.product_id.id),
                    Domain("state", "not in", ["done", "cancel"]),
                    Domain("quantity_product_uom", ">", 0),
                    Domain("location_id", "=", self.location_id.id),
                    Domain("lot_id", "=", self.lot_id.id),
                    Domain("owner_id", "=", self.owner_id.id),
                ]
            ),
        }
        return action
