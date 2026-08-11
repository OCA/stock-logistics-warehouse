from odoo import models
from odoo.tools import float_compare, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)
        if self._context.get("changed_purchase_method"):
            vals.update(procure_method="make_to_order")
        return vals

    def _split(self, qty, restrict_partner_id=False):
        new_move_vals = super()._split(qty, restrict_partner_id=restrict_partner_id)
        if self._context.get("changed_purchase_method"):
            self.write({"procure_method": "make_to_stock"})
        return new_move_vals

    def _adjust_procure_method(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        no_split_procurement_moves = self.browse([])
        for move in self:
            product_id = move.product_id
            domain = [
                ("location_src_id", "=", move.location_id.id),
                ("location_dest_id", "=", move.location_dest_id.id),
                ("action", "!=", "push"),
            ]
            rules = self.env["procurement.group"]._search_rule(
                False, move.product_packaging_id, product_id, move.warehouse_id, domain
            )
            if not rules or rules and rules.action != "split_procurement":
                no_split_procurement_moves |= move
            else:
                needed_qty = rules.get_mto_qty_to_order(
                    product_id, move.product_qty, move.product_uom, {}
                )
                if (
                    float_compare(
                        needed_qty, move.product_qty, precision_digits=precision
                    )
                    == 0.0
                ):
                    move.procure_method = "make_to_order"
                elif move.state == "draft":
                    # In case of partial stock, we need to split the move but Odoo
                    # won't allow it unless the move is already confirmed. So we leave
                    # it as make_to_stock to allow reservation and split it after its
                    # confirmation.
                    move.procure_method = "make_to_stock"
                else:
                    self.create(
                        move.with_context(changed_purchase_method=True)._split(
                            needed_qty
                        )
                    )
                    move._action_assign()
        if no_split_procurement_moves:
            return super(StockMove, no_split_procurement_moves)._adjust_procure_method()

    def _action_confirm(self, merge=True, merge_into=False):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        moves_to_split = {}
        for move in self:
            if (
                move.state == "draft"
                and move.procure_method == "make_to_stock"
                and move.raw_material_production_id
            ):
                domain = [
                    ("location_src_id", "=", move.location_id.id),
                    ("location_dest_id", "=", move.location_dest_id.id),
                    ("action", "!=", "push"),
                ]
                rules = self.env["procurement.group"]._search_rule(
                    False,
                    move.product_packaging_id,
                    move.product_id,
                    move.warehouse_id,
                    domain,
                )
                if not rules or rules and rules.action != "split_procurement":
                    continue
                needed_qty = rules.get_mto_qty_to_order(
                    move.product_id, move.product_qty, move.product_uom, {}
                )
                if not float_is_zero(needed_qty, precision_digits=precision):
                    moves_to_split[move] = needed_qty
        res = super()._action_confirm(merge=merge, merge_into=merge_into)
        for move, qty_to_split in moves_to_split.items():
            if (
                not move.exists()
                or move.state in ["draft", "cancel", "done"]
                or move.procure_method != "make_to_stock"
                or not move.raw_material_production_id
            ):
                continue
            move._do_unreserve()
            self.create(
                move.with_context(changed_purchase_method=True)._split(qty_to_split)
            )._action_confirm()
            move._action_assign()
        return res
