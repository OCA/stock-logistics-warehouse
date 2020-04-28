# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        unassigned = self.filtered(
            lambda m: m.state not in ("assigned", "partially_available", "done")
        )
        super()._action_assign()
        unassigned.filtered(
            lambda m: m.state in ("assigned", "partially_available")
        )._sync_same_destination_orig_moves()

    @staticmethod
    def _filter_sync_destination(move):
        return move.picking_id.picking_type_id.sync_common_move_dest_location

    def _sync_same_destination_orig_moves(self):
        moves = self.filtered(self._filter_sync_destination)
        for move in moves.mapped("move_orig_ids"):
            neighbour_moves = move.common_dest_move_ids
            move._sync_destination_to_neighbour_moves(neighbour_moves)

    def _sync_destination_to_neighbour_moves(self, neighbour_moves):
        self.ensure_one()
        # get the destination of the first move which was done, we want all the other
        # moves, available or not, so all the goods will be moved to the same place
        destination = self.move_line_ids.mapped("location_dest_id")
        # moves destination locations are restricted to the same destination,
        # so user can't bring goods elsewhere than the good already moved
        neighbour_moves.filtered(
            lambda m: m.location_dest_id != destination and m.state != "done"
        ).write({"location_dest_id": destination.id})
        lines = neighbour_moves.mapped("move_line_ids")
        lines.filtered(
            lambda l: l.location_dest_id != destination and l.state != "done"
        ).write({"location_dest_id": destination.id})
