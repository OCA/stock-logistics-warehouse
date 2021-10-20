# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _adjust_procure_method(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            product_id = move.product_id
            domain = [
                ("location_src_id", "=", move.location_id.id),
                ("location_id", "=", move.location_dest_id.id),
                ("action", "!=", "push"),
            ]
            rules = self.env["procurement.group"]._search_rule(
                False, product_id, move.warehouse_id, domain
            )
            if not rules or rules and rules.action != "split_procurement":
                return super()._adjust_procure_method()
            needed_qty = rules.get_mto_qty_to_order(
                move.product_id, move.product_qty, move.product_uom, {}
            )
            if float_is_zero(needed_qty, precision_digits=precision):
                move.procure_method = "make_to_stock"
            elif (
                float_compare(needed_qty, move.product_qty, precision_digits=precision)
                == 0.0
            ):
                move.procure_method = "make_to_order"
            else:
                mts_qty = move.product_uom_qty - needed_qty
                move.copy(
                    {
                        "product_uom_qty": needed_qty,
                        "procure_method": "make_to_order",
                    }
                )
                move.write(
                    {"product_uom_qty": mts_qty, "procure_method": "make_to_stock"}
                )
                move._action_assign()
