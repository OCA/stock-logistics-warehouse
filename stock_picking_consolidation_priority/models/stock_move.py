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
           INT/001 ━► PICK/003 ┛

        If the flag "consolidate_priority" is set on the picking type of OUT,
        as soon as one of the move of PACK/001 or PACK/002 is done, all the
        moves of the INT, 3 PICK, and the 2 PACK must be returned to have their
        priority raised, as we want to consolidate everything asap in OUT/001.

        If the flag is set on PACK and one move in PICK/001 is set to done,
        other moves of PICK/001 are returned to finish PACK/001.

        If the flag is set on PACK and one move in PICK/002 is set to done, all
        the moves of INT/001 and PICK/003 and the other moves of PICK/002 have
        to be returned as they will help to consolidate PACK/002.


        If the flag is set on PACK, when a move in INT/001 is set to done,
        nothing happens, but when a move in PICK/003 is set to done, all the
        moves of INT/001 and PICK/002 and the other moves of PICK/003 have to
        be returned as they will help to consolidate PACK/002.

        If the flag is set on both PACK and OUT, the result is the same as the
        first case: all PICK and PACK are returned.
        """
        query = """
        WITH RECURSIVE
        -- For every destination move for which we have the flag set, walk back
        -- through stock_move_move_rel to find all the origin moves
        origins (id, picking_id, is_consolidation_dest) AS (
            -- Find the destination move of the current moves which have the flag
            -- consolidate_priority on their picking type. From there, find all
            -- the other moves of the consolidation transfer.
            -- They are the starting point to search the origin moves.
            -- In the final query, the rows with "consolidate_priority" equal
            -- to true are excluded, because we want to raise the priority of
            -- the moves *before* the picking type with the flag
            SELECT consolidation_dest_moves.id,
                   stock_picking.id,
                   stock_picking_type.consolidate_priority as is_consolidation_dest
            FROM stock_move_move_rel
            INNER JOIN stock_move move_dest
            ON move_dest.id = stock_move_move_rel.move_dest_id
            INNER JOIN stock_picking
            ON stock_picking.id = move_dest.picking_id
            -- select *all* the moves of the transfer with the consolidation flag,
            -- origin moves will be searched for all of them in the recursive part
            INNER JOIN stock_move consolidation_dest_moves
            ON consolidation_dest_moves.picking_id = stock_picking.id
            INNER JOIN stock_picking_type
            ON stock_picking_type.id = stock_picking.picking_type_id
            WHERE stock_move_move_rel.move_orig_id IN %s
            AND stock_picking_type.consolidate_priority = true

            -- We use union here to keep duplicate in case a move both has the
            -- flag "consolidate_priority" on its picking type AND is the
            -- origin move for another move with the flag (e.g, option
            -- activated both on PACK and OUT). Anyway, the final query filters
            -- on the second part of the union.
            UNION ALL

            -- recurse to find all the origin moves which have a destination that
            -- needs priority consolidation
            SELECT move_orig.id,
                   move_orig.picking_id,
                   false as is_consolidation_dest
            FROM stock_move move_orig
            INNER JOIN stock_move_move_rel
            ON move_orig.id = stock_move_move_rel.move_orig_id
            INNER JOIN origins
            ON origins.id = stock_move_move_rel.move_dest_id
        )
        SELECT id FROM origins WHERE is_consolidation_dest = false
        """
        return (query, (tuple(self.ids),))

    def _consolidate_priority_domain(self):
        return [("state", "not in", ("cancel", "done"))]

    def _consolidate_priority_values(self):
        return {"priority": self._consolidate_priority_value}

    def _consolidate_priority(self):
        self.flush(["move_dest_ids", "move_orig_ids", "picking_id"])
        self.env["stock.picking"].flush(["picking_type_id"])
        self.env["stock.picking.type"].flush(["consolidate_priority"])
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
