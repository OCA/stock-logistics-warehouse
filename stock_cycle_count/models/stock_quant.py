# Copyright 2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # pylint: disable=W8110
    def _apply_inventory(self):
        accuracy_dict = {}
        theoretical_dict = {}
        counted_dict = {}
        StockMoveLine = self.env["stock.move.line"]
        for quant in self:
            if quant.discrepancy_percent > 100:
                line_accuracy = 0
            else:
                line_accuracy = 1 - (quant.discrepancy_percent / 100)
            accuracy_dict[quant.id] = line_accuracy
            theoretical_dict[quant.id] = quant.quantity
            counted_dict[quant.id] = quant.inventory_quantity
        super()._apply_inventory()
        for quant in self:
            domain = [
                ("product_id", "=", quant.product_id.id),
                ("lot_id", "=", quant.lot_id.id),
                "|",
                ("location_id", "=", quant.location_id.id),
                ("location_dest_id", "=", quant.location_id.id),
            ]
            if quant.company_id:
                domain.append(("company_id", "=", quant.company_id.id))
            move_lines = StockMoveLine.search(domain, order="create_date asc")
            if move_lines:
                last_move_line = move_lines[-1]
                last_move_line.write(
                    {
                        "line_accuracy": accuracy_dict[quant.id],
                        "theoretical_qty": theoretical_dict[quant.id],
                        "counted_qty": counted_dict[quant.id],
                    }
                )
