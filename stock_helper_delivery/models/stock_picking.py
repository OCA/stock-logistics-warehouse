# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


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

        def get_first_move_dest(moves):
            for move in moves.move_dest_ids:
                if move.state not in ("cancel", "done"):
                    return move

        move_dest = get_first_move_dest(self.move_lines)
        while move_dest:
            if move_dest.picking_id.carrier_id:
                return move_dest.picking_id
            move_dest = get_first_move_dest(move_dest)
        # Should return an empty record if we reach this line
        return self.browse()
