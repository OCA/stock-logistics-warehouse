from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    to_do = fields.Boolean(default=True)

    def _apply_inventory(self):
        res = super()._apply_inventory()
        record_moves = self.env["stock.move.line"]
        for rec in self:
            adjustment = (
                self.env["stock.inventory"]
                .search([("state", "=", "in_progress")])
                .filtered(
                    lambda x: rec.location_id in x.location_ids
                    or rec.location_id in x.location_ids.child_ids
                )
            )
            moves = record_moves.search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("lot_id", "=", rec.lot_id.id),
                    ("company_id", "=", rec.company_id.id),
                    "|",
                    ("location_id", "=", rec.location_id.id),
                    ("location_dest_id", "=", rec.location_id.id),
                ],
                order="create_date asc",
            )
            move = moves[len(moves) - 1]
            adjustment.stock_move_ids |= move
            move.inventory_adjustment_id = adjustment
            rec.to_do = False
        return res

    @api.model
    def _unlink_zero_quants(self):
        # Prevents unlinking of the quants until the inventory adjustments are completed
        # inherit the method _unlink_zero_quants without totally overwrite is not
        # possible witohut a hook.
        to_do_quants = self.env["stock.quant"].search([("to_do", "=", True)])
        if to_do_quants:
            return True
        else:
            return super()._unlink_zero_quants()
