# Copyright 2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _apply_inventory(self):
        accuracy_dict = {}
        theoretical_dict = {}
        counted_dict = {}
        for rec in self:
            if rec.discrepancy_percent > 100:
                line_accuracy = 0
            else:
                line_accuracy = 1 - (rec.discrepancy_percent / 100)
            accuracy_dict[rec.id] = line_accuracy
            theoretical_dict[rec.id] = rec.quantity
            counted_dict[rec.id] = rec.inventory_quantity
        res = super()._apply_inventory()
        for rec in self:
            record_moves = self.env["stock.move.line"]
            moves = record_moves.search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("lot_id", "=", rec.lot_id.id),
                    "|",
                    ("location_id", "=", rec.location_id.id),
                    ("location_dest_id", "=", rec.location_id.id),
                ]
                + ([("company_id", "=", rec.company_id.id)] if rec.company_id else []),
                order="create_date asc",
            )
            move = moves[len(moves) - 1]
            move.write(
                {
                    "line_accuracy": accuracy_dict[rec.id],
                    "theoretical_qty": theoretical_dict[rec.id],
                    "counted_qty": counted_dict[rec.id],
                }
            )
        return res
