# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        to_sync = {}
        for move in self:
            # store the original moves that goes in the same transfer, because
            # when we call super(), changes made to the chain of moves (for
            # instance the application of a "dynamic routing" by
            # stock_dynamic_routing) may happen.
            if move.move_dest_ids.filtered(self._filter_sync_destination):
                to_sync[move] = move.common_dest_move_ids

        # When using dynamic routing, it will be applied applied during the
        # call to super. The routing can move a stock.move to another
        # stock.picking, insert a new stock.move...
        # We have to apply the synchronization of the destinations once the
        # move is done to be sure it was really the selected destination, and a
        # user started to move goods at this place.
        moves_todo = super()._action_done(cancel_backorder=cancel_backorder)

        for move, neighbours in to_sync.items():
            if move.state != "done":
                continue

            # if any new move were added (split, extra move, ...) we have to
            # synchronize their destination location as well
            neighbours |= move.common_dest_move_ids

            # find the location where the neighbour moves (eg. the moves which
            # have to be packed together, so moved at the same place) amongst
            # the destination moves. We consider only assigned moves, which
            # means part of the goods have been moved there.
            dest_move = move.move_dest_ids.filtered(
                lambda m: m.state in ("assigned", "partially_available")
                and self._filter_sync_destination(m)
            )
            dest_move = fields.first(dest_move)
            dest_move_line = fields.first(dest_move.move_line_ids)

            # Sync the destinations to group the moves in the same
            # location. If a routing was applied to the assigned move,
            # the other waiting moves will now match the same routing
            # which will be applied.
            move._sync_destination_to_neighbour_moves(
                neighbours, dest_move_line.location_id
            )
        return moves_todo

    @staticmethod
    def _filter_sync_destination(move):
        return move.picking_id.picking_type_id.sync_common_move_dest_location

    def _sync_destination_to_neighbour_moves(self, neighbour_moves, destination):
        self.ensure_one()
        neighbour_moves = neighbour_moves.filtered(lambda m: m.state != "done")
        # Normally the move destination does not change. But when using other
        # addons, such as stock_dynamic_routing, the source location of the
        # destination move can change, so handle this case too. (there is a
        # glue module stock_dynamic_routing_common_dest_sync).
        moves_to_update = (self | neighbour_moves).filtered(
            lambda m: m.location_dest_id != destination
        )
        moves_to_update.write({"location_dest_id": destination.id})
        # Sync the source of the destination move too, if it's still waiting.
        moves_to_update.move_dest_ids.filtered(
            lambda m: (
                m.state == "waiting"
                or m.state == "assigned"
                and m in self.move_dest_ids
            )
            and m.location_id != destination
        ).write({"location_id": destination.id})
        lines = neighbour_moves.mapped("move_line_ids")
        lines.filtered(
            lambda l: l.location_dest_id != destination and l.state != "done"
        ).write({"location_dest_id": destination.id})
