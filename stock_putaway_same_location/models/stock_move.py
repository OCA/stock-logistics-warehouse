from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        if reserved_quant:
            # Provide a lot id for further use in a `putaway_apply` method
            self = self.with_context(
                lot_id=reserved_quant.lot_id.id,
                current_move_id=self.id,
            )
        return super(StockMove, self)._prepare_move_line_vals(
            quantity, reserved_quant)
