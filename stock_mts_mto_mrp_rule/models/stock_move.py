from odoo import models
from odoo.tools import float_compare, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_split_vals(self, qty):
        vals = super(StockMove, self)._prepare_move_split_vals(qty)
        if self._context.get("changed_purchase_method"):
            vals.update(procure_method="make_to_order")
        return vals

    def _split(self, qty, restrict_partner_id=False):
        new_move_vals = super(StockMove, self)._split(
            qty, restrict_partner_id=restrict_partner_id
        )
        if self._context.get("changed_purchase_method"):
            self.write({"procure_method": "make_to_stock"})
        return new_move_vals

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
                super(StockMove, move)._adjust_procure_method()
            else:
                needed_qty = rules.get_mto_qty_to_order(
                    product_id, move.product_qty, move.product_uom, {}
                )
                if float_is_zero(needed_qty, precision_digits=precision):
                    move.procure_method = "make_to_stock"
                elif (
                    float_compare(
                        needed_qty, move.product_qty, precision_digits=precision
                    )
                    == 0.0
                ):
                    move.procure_method = "make_to_order"
                else:
                    self.create(
                        move.with_context(changed_purchase_method=True)._split(
                            needed_qty
                        )
                    )
                    move._action_assign()
