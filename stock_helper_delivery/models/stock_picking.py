# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_carrier_from_chained_picking(self):
        """Returns the proper carrier for the current transfer.

        For non-delivery transfers this method will return the carrier used
        on the related delivery transfer if there is one.
        """
        self.ensure_one()
        if self.carrier_id:
            return self.carrier_id

        def get_moves_dest(moves):
            return moves.move_dest_ids.filtered(
                lambda m: m.state not in ("cancel", "done")
            )

        moves_dest = get_moves_dest(self.move_lines)
        while moves_dest:
            carrier = moves_dest.picking_id.carrier_id
            if carrier:
                return fields.first(carrier)
            moves_dest = get_moves_dest(moves_dest)
        # Should return an empty record if we reach this line
        return self.carrier_id
