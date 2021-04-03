# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


def get_first_move_dest(moves, done=False):
    move_states = ("cancel", "done")
    for move in moves.move_dest_ids:
        if move.state in move_states if done else move.state not in move_states:
            return move


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_picking_with_carrier_from_chain(self):
        """Returns a picking with a carrier among next chained pickings.

        For non-delivery transfers this method will often return the related
        delivery.
        """
        self.ensure_one()
        if self.carrier_id:
            return self

        move_dest = get_first_move_dest(self.move_lines)
        while move_dest:
            if move_dest.picking_id.carrier_id:
                return move_dest.picking_id
            move_dest = get_first_move_dest(move_dest)
        # Should return an empty record if we reach this line
        return self.browse()

    def _get_ship_from_chain(self, done=False):
        """Returns the shipment related to the current operation."""
        move_dest = get_first_move_dest(self.move_lines, done=done)
        while move_dest:
            picking = move_dest.picking_id
            if picking.picking_type_id.code == "outgoing":
                return picking
            move_dest = get_first_move_dest(move_dest, done=done)
        # Should return an empty record if we reach this line
        return self.browse()
