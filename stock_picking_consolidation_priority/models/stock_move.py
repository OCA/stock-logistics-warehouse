# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.osv import expression


class StockMove(models.Model):
    _inherit = "stock.move"

    _consolidate_priority_value = "3"

    def _action_done(self, cancel_backorder=False):
        moves_to_check = super()._action_done(cancel_backorder=cancel_backorder)
        moves_to_check.filtered(lambda move: move.state == "done")
        if moves_to_check:
            moves_to_check._consolidate_priority()
        return moves_to_check

    def _query_get_consolidate_moves(self):
        """Return a query to find the moves to consolidate in priority

        Consider this chain of moves::

            PICK/001 ━►  PACK/001  ┓
                                   ┃
            PICK/002 ┓             ┣━► OUT/001
                     ┣━► PACK/002  ┛
            PICK/003 ┛

        If the flag "consolidate_priority" is set on the picking type of OUT,
        when we set any of the PICK to done, the 3 PICK and the 2 PACK must
        be returned to have their priority raised.

        If the flag is set on PACK and PICK/002 or PICK/003 is set to done, the
        other PICK that leads to PACK/002 must be returned to have its priority
        raised. But if only PICK/001 is set to done, nothing is returned.

        If the flag is set on both PACK and OUT, the result is the same as the
        first case: all PICK and PACK are returned.
        """
        query = """
        WITH RECURSIVE

        -- Walk through all relations in stock_move_move_rel to find the
        -- destination moves. For each move, join on stock_picking_type
        -- to check if the flag "consolidate_priority" is set
        destinations (id, consolidate_origins) AS (
            -- starting move
            SELECT stock_move.id,
                   -- the moves here are done: their origin moves are
                   -- supposed to be done too, we don't need to raise their
                   -- priority
                   false as consolidate_origins
            FROM stock_move
            WHERE stock_move.id IN %s
            UNION
            -- recurse to find all the destinations
            SELECT move_dest.id,
                   stock_picking_type.consolidate_priority as consolidate_origins
            FROM stock_move move_dest
            INNER JOIN stock_move_move_rel
            ON move_dest.id = stock_move_move_rel.move_dest_id
            INNER JOIN stock_picking
            ON stock_picking.id = move_dest.picking_id
            INNER JOIN stock_picking_type
            ON stock_picking_type.id = stock_picking.picking_type_id
            INNER JOIN destinations
            ON destinations.id = stock_move_move_rel.move_orig_id
        ),

        -- For every destination move for which we have the flag set, walk back
        -- through stock_move_move_rel to find all the origin moves
        origins (id, consolidate_origins) AS (
            -- for all the destinations which have to consolidate their origins,
            -- it finds all the origin moves, in the final query, the rows with
            -- "consolidate_origins" equal to true are excluded, because we want
            -- to raise the priority of the moves *before* the picking type with
            -- the flag
            SELECT destinations.id, true
            FROM destinations
            WHERE consolidate_origins = true
            -- We use union here to keep duplicate in case a move both has the flag
            -- "consolidate_priority" on its picking type AND is the origin move
            -- for another move with the flag. Anyway, the final query filters
            -- on the second part of the union.
            UNION ALL
            -- recurse to find all the origin moves which have a destination that
            -- needs priority consolidation
            SELECT move_orig.id, false
            FROM stock_move move_orig
            INNER JOIN stock_move_move_rel
            ON move_orig.id = stock_move_move_rel.move_orig_id
            INNER JOIN origins
            ON origins.id = stock_move_move_rel.move_dest_id
        )
        SELECT DISTINCT id FROM origins
        WHERE consolidate_origins = false
        """
        return (query, (tuple(self.ids),))

    def _consolidate_priority_domain(self):
        return [("state", "not in", ("cancel", "done"))]

    def _consolidate_priority_values(self):
        return {"priority": self._consolidate_priority_value}

    def _consolidate_priority(self):
        query, params = self._query_get_consolidate_moves()
        self.env.cr.execute(query, params)
        move_ids = [row[0] for row in self.env.cr.fetchall()]
        if not move_ids:
            return
        moves = self.search(
            expression.AND(
                [[("id", "in", move_ids)], self._consolidate_priority_domain()]
            )
        )
        moves.write(self._consolidate_priority_values())
