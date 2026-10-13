# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict
from operator import itemgetter

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero, float_round


class StockMove(models.Model):
    _inherit = ["stock.move", "product.secondary.unit.mixin"]
    _name = "stock.move"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }

    product_uom_qty = fields.Float(
        store=True, readonly=False, compute="_compute_product_uom_qty", copy=True
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_uom_qty(self):
        self._compute_helper_target_field_qty()

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        """Don't merge moves with distinct secondary units"""
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields += ["secondary_uom_id"]
        return distinct_fields

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res["secondary_uom_id"] = self.secondary_uom_id.id
        res["secondary_uom_qty"] = self.secondary_uom_qty
        return res

    def _prepare_extra_move_vals(self, qty):
        vals = super()._prepare_extra_move_vals(qty)
        if self.secondary_uom_id:
            vals["secondary_uom_id"] = self.secondary_uom_id.id
            # Get difference between demand secondary qty and done secondary qty
            vals["secondary_uom_qty"] = (
                sum(self.move_line_ids.mapped("secondary_uom_qty"))
                - self.secondary_uom_qty
            )
        return vals

    def _merge_moves(self, merge_into=False):
        """Set the last secondary uom qty when merge negative stock move"""
        # We have to do this when merging negative moves because the positive ones call
        # _merge_moves_fields but the negative ones accumulate inside this method.

        distinct_fields = self._prepare_merge_moves_distinct_fields()
        excluded_fields = self._prepare_merge_negative_moves_excluded_distinct_fields()
        neg_key = itemgetter(
            *[field for field in distinct_fields if field not in excluded_fields]
        )
        neg_qty_moves_dic = defaultdict(float)
        # Dependent secondary units are recomputed by core when product_uom_qty
        # of the absorbing move is updated, so only independent ones are needed.
        for move in self:
            if move.secondary_uom_id.dependency_type == "independent" and (
                float_compare(
                    move.secondary_uom_qty,
                    0.0,
                    precision_rounding=move.secondary_uom_id.uom_id.rounding or 0.01,
                )
                < 0
            ):
                neg_qty_moves_dic[neg_key(move)] += move.secondary_uom_qty
        if not neg_qty_moves_dic:
            return super()._merge_moves(merge_into=merge_into)
        # Positive moves fully consumed by negative ones are left with zero quantity
        # and are not returned by super, so we have to keep them to reset them.
        candidate_moves_list = []
        if merge_into:
            candidate_moves_list.append(merge_into | self)
        else:
            self._update_candidate_moves_list(candidate_moves_list)
        pos_moves = self.browse()
        for candidate_moves in candidate_moves_list:
            pos_moves |= candidate_moves.filtered(
                lambda m: neg_key(m) in neg_qty_moves_dic
                and float_compare(
                    m.product_uom_qty, 0.0, precision_rounding=m.product_uom.rounding
                )
                > 0
            )
        res = super()._merge_moves(merge_into=merge_into)
        for move in res:
            secondary_uom_qty = neg_qty_moves_dic.get(neg_key(move))
            if secondary_uom_qty is not None:
                if move.product_uom_qty >= 0.0:
                    new_secondary_uom_qty = move.secondary_uom_qty + secondary_uom_qty
                else:
                    # Alternatively we must get values from candidate moves before
                    # merge for all cases and it has poor performance.
                    # Don't use _compute_secondary_uom_qty() because it skips
                    # independent secondary units
                    new_secondary_uom_qty = move._get_secondary_uom_qty_from_uom_qty()
                # Use _write to avoid recompute product_uom_qty
                move._write({"secondary_uom_qty": new_secondary_uom_qty})
                move.invalidate_cache(fnames=["secondary_uom_qty"])
        zero_qty_moves = pos_moves.exists().filtered(
            lambda m: m.secondary_uom_qty
            and float_is_zero(
                m.product_uom_qty, precision_rounding=m.product_uom.rounding
            )
        )
        zero_qty_moves._write({"secondary_uom_qty": 0.0})
        zero_qty_moves.invalidate_cache(fnames=["secondary_uom_qty"])
        return res

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super()._action_confirm(merge=merge, merge_into=merge_into)
        # Core turns the remaining negative moves into returns flipping only the sign
        # of product_uom_qty, so independent secondary quantities keep the old sign.
        for move in moves.filtered(
            lambda m: m.secondary_uom_id.dependency_type == "independent"
            and m.secondary_uom_qty < 0.0 < m.product_uom_qty
        ):
            # Use _write to avoid recompute product_uom_qty
            move._write({"secondary_uom_qty": -move.secondary_uom_qty})
            move.invalidate_cache(fnames=["secondary_uom_qty"])
        return moves

    # Update secondary quantity in moves when backorder is created
    def _split(self, qty, restrict_partner_id=False):
        res = super()._split(qty, restrict_partner_id)
        done_secondary_qty = sum(self.move_line_ids.mapped("secondary_uom_qty"))
        # Use _write to avoid recompute product_uom_qty
        self._write({"secondary_uom_qty": done_secondary_qty})
        self.invalidate_cache(fnames=["secondary_uom_qty"])
        for vals in res:
            new_secondary_qty = vals.get("secondary_uom_qty", 0.0)
            if new_secondary_qty > self.secondary_uom_qty:
                vals["secondary_uom_qty"] = float_round(
                    new_secondary_qty - done_secondary_qty,
                    precision_rounding=self.secondary_uom_id.uom_id.rounding or 0.01,
                )
        return res


class StockMoveLine(models.Model):
    _inherit = ["stock.move.line", "product.secondary.unit.mixin"]
    _name = "stock.move.line"
    _secondary_unit_fields = {"qty_field": "qty_done", "uom_field": "product_uom_id"}

    qty_done = fields.Float(store=True, readonly=False, compute="_compute_qty_done")

    @api.model
    def create(self, vals):
        move = self.env["stock.move"].browse(vals.get("move_id", False))
        if move.secondary_uom_id:
            vals["secondary_uom_id"] = move.secondary_uom_id.id
        return super().create(vals)

    @api.depends("secondary_uom_id", "secondary_uom_qty")
    def _compute_qty_done(self):
        self._compute_helper_target_field_qty()
