# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from .stock_move import COUNT_PRESERVING_DEPENDENCY_TYPES


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        vals = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        # secondary_uom_qty has copy=False (an active push chain must never
        # inherit a stale count from a cancelled/superseded move), so a
        # pushed move (e.g. the "ship" move of a pick_ship route) is
        # created with it empty by default. For a count-preserving
        # secondary unit, that empty value then gets filled in by the
        # factor-based fallback (_onchange_helper_product_uom_for_secondary,
        # triggered by _action_confirm) - a weight-derived guess, exactly
        # what this dependency type exists to avoid. Carry the real count
        # forward explicitly instead of losing it to copy=False.
        if (
            move_to_copy.secondary_uom_id
            and move_to_copy.secondary_uom_id.dependency_type
            in COUNT_PRESERVING_DEPENDENCY_TYPES
        ):
            # Core pushes `quantity` (what was actually PROCESSED, summed
            # from the move lines) as the new move's demand, never
            # `product_uom_qty` - only what really moved travels down the
            # chain. Mirror that on the secondary unit: take the counted
            # pieces from the move lines, not the move's own demand field.
            # Both agree when a backorder was created, since
            # _prepare_move_split_vals() already resynced the move's own
            # demand to what was processed. They diverge when the user
            # finalizes with "No Backorder" (`cancel_backorder=True`):
            # there is no split at all, so core leaves product_uom_qty at
            # the full original demand and the move keeps demanding 40
            # pieces while only 30 were ever counted - pushing that would
            # send a piece count downstream that never physically existed
            # (22 kg shipped as 40 pieces), and a later merge would add it
            # on top of the next push.
            done_secondary_qty = move_to_copy.secondary_uom_qty_done
            # Nothing counted at all - the operator validated straight from
            # the reservation without touching the secondary unit. Fall
            # back to the demand, same as
            # _onchange_helper_product_uom_for_secondary() does.
            vals["secondary_uom_qty"] = (
                done_secondary_qty or move_to_copy.secondary_uom_qty
            )
        return vals
