# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

# Secondary unit dependency types that must survive a split/backorder as an
# exact count, never a proportional recompute from the primary quantity.
COUNT_PRESERVING_DEPENDENCY_TYPES = ("independent", "secondary_priority")


class StockMove(models.Model):
    _inherit = ["stock.move", "product.secondary.unit.mixin"]
    _name = "stock.move"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }

    product_uom_qty = fields.Float(
        store=True,
        readonly=False,
        compute="_compute_product_uom_qty",
        copy=True,
        precompute=True,
    )
    secondary_uom_qty = fields.Float(copy=False)
    # Core has both a demand (product_uom_qty) and a done aggregate
    # (quantity, computed from move_line_ids.quantity) on stock.move. The
    # secondary unit only ever got the demand half - this mirrors the done
    # half, the same way quantity does, so code that needs "how many pieces
    # were actually done" doesn't have to re-derive it ad hoc every time.
    secondary_uom_qty_done = fields.Float(
        compute="_compute_secondary_uom_qty_done",
        store=True,
        digits="Product Unit of Measure",
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_uom_qty(self):
        self._compute_helper_target_field_qty()

    @api.depends("move_line_ids.secondary_uom_qty")
    def _compute_secondary_uom_qty_done(self):
        for move in self:
            move.secondary_uom_qty_done = sum(
                move.move_line_ids.mapped("secondary_uom_qty")
            )

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    def _onchange_helper_product_uom_for_secondary(self):
        # A count-preserving secondary unit (e.g. pieces vs. weight) must
        # never be recomputed from the primary quantity - that's the whole
        # point of "independent"/"secondary_priority" vs. "dependent".
        # _prepare_move_split_vals() already sets an exact value for it on
        # a backorder; only fall back to the factor-based estimate when
        # nothing set it yet (e.g. a brand new line), same as "dependent"
        # would.
        if (
            self.secondary_uom_id
            and self.secondary_uom_id.dependency_type
            in COUNT_PRESERVING_DEPENDENCY_TYPES
        ):
            if not self.secondary_uom_qty:
                qty_line = self._get_quantity_from_line()
                self.secondary_uom_qty = self._convert_qty_to_secondary_uom(qty_line)
            return
        return super()._onchange_helper_product_uom_for_secondary()

    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)
        if (
            self.secondary_uom_id
            and self.secondary_uom_id.dependency_type
            in COUNT_PRESERVING_DEPENDENCY_TYPES
        ):
            # Keep the secondary unit an exact count across the split: the
            # backorder gets exactly what's left of the demand, not a
            # proportional recompute from the (possibly unrelated) primary
            # quantity split off - e.g. 40 pieces demanded, 30 actually
            # picked regardless of their real weight -> the backorder is
            # for 10 pieces, never a weight-based estimate.
            done_secondary_qty = self.secondary_uom_qty_done
            vals["secondary_uom_qty"] = max(
                self.secondary_uom_qty - done_secondary_qty, 0.0
            )
            # `self` becomes the "done" move after the split (core just
            # reduced its product_uom_qty to what was processed) - keep its
            # own secondary unit qty in sync with that instead of the stale
            # original demand. For "secondary_priority", a plain write
            # would retrigger _compute_product_uom_qty (it depends on
            # secondary_uom_qty) and clobber the just-set real weight with
            # a factor-based estimate - use _write()/invalidate_recordset()
            # to bypass that recompute, like the (now-upstreamed) private
            # fix this is based on used to.
            self._write({"secondary_uom_qty": done_secondary_qty})
            self.invalidate_recordset(fnames=["secondary_uom_qty"])
        return vals

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        """Don't merge moves with distinct secondary units"""
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields += ["secondary_uom_id"]
        return distinct_fields

    def _merge_moves_fields(self):
        # Core sums product_uom_qty across the moves being merged (e.g. a
        # 2nd push move created from a backorder) but has no notion of
        # secondary_uom_qty at all, so it silently keeps whatever the
        # surviving move already had - losing the backorder's pieces on
        # every merge. _prepare_merge_moves_distinct_fields() above already
        # guarantees every move in self shares the same secondary_uom_id.
        vals = super()._merge_moves_fields()
        secondary_uom = self[:1].secondary_uom_id
        if (
            secondary_uom
            and secondary_uom.dependency_type in COUNT_PRESERVING_DEPENDENCY_TYPES
        ):
            merge_extra = self.env.context.get("merge_extra")
            vals["secondary_uom_qty"] = (
                sum(self.mapped("secondary_uom_qty"))
                if not merge_extra
                else self[0].secondary_uom_qty
            )
        return vals

    def _recompute_state(self):
        # Override when creating backorder
        # to update secondary unit quantities
        res = super()._recompute_state()
        for move in self:
            move.onchange_product_uom_for_secondary()
        return res


class StockMoveLine(models.Model):
    _inherit = ["stock.move.line", "product.secondary.unit.mixin"]
    _name = "stock.move.line"
    _secondary_unit_fields = {"qty_field": "quantity", "uom_field": "product_uom_id"}

    quantity = fields.Float(
        store=True, readonly=False, compute="_compute_quantity", precompute=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            move = self.env["stock.move"].browse(vals.get("move_id", False))
            if move.secondary_uom_id:
                vals["secondary_uom_id"] = move.secondary_uom_id.id
        return super().create(vals_list)

    @api.depends("secondary_uom_id", "secondary_uom_qty")
    def _compute_quantity(self):
        # On a move LINE, `quantity` is the actually measured/counted
        # amount, not a demand estimate - "secondary_priority" must behave
        # like "independent" here (never overwritten once set), even
        # though it behaves like "dependent" for the DEMAND field on
        # stock.move (product_uom_qty) above. "independent" itself already
        # gets this protection from the mixin's own helper, no need to
        # special-case it here too.
        already_measured = self.filtered(
            lambda line: line.secondary_uom_id
            and line.secondary_uom_id.dependency_type == "secondary_priority"
            and line.quantity
        )
        (self - already_measured)._compute_helper_target_field_qty()

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        for move_line in self:
            line_key = self._get_aggregated_properties(move_line=move_line)["line_key"]
            aggregated_move_lines[line_key]["secondary_uom_qty"] = (
                move_line.secondary_uom_qty
            )
            aggregated_move_lines[line_key]["secondary_uom_id"] = (
                move_line.secondary_uom_id
            )

        return aggregated_move_lines
