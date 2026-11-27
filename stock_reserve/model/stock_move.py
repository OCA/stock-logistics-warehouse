# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _reserve_lots(self, lots_data, strict=False):
        """Reserve the move only from the given lots, in the given order.

        :param lots_data: list of tuples ``(lot, location, quantity)``, where
            ``quantity`` is the maximum quantity to take from that lot in the
            product UoM, or ``None`` to take all the available quantity.
        :param strict: if True, only take quants of exactly that location.
        """
        self.ensure_one()
        Quant = self.env["stock.quant"]
        rounding = self.product_id.uom_id.rounding
        need = self.product_qty - sum(self.move_line_ids.mapped("reserved_qty"))
        for lot, location, quantity in lots_data:
            if float_compare(need, 0, precision_rounding=rounding) <= 0:
                break
            available = Quant._get_available_quantity(
                self.product_id, location, lot_id=lot, strict=strict
            )
            take = min(available, need)
            if quantity is not None:
                take = min(take, quantity)
            if float_compare(take, 0, precision_rounding=rounding) <= 0:
                continue
            need -= self._update_reserved_quantity(
                take, take, location, lot_id=lot, strict=strict
            )
        self._recompute_state()
