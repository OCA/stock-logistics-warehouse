# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    @api.multi
    def change_prod_qty(self):
        moves = self.mo_id.mapped('move_raw_ids').filtered(
            lambda m: m.procure_method == 'make_to_order')
        move_lines = moves.mapped('move_line_ids')
        moves.write({
            'state': 'draft',
        })
        move_lines.write({
            'state': 'draft',
        })
        moves.unlink()
        res = super().change_prod_qty()
        # If a MTO move was deleted, the method change_prod_qty creates a new
        # move for the component, but it's in draft state and cannot be
        # reserved, we need to confirm the stock.move
        self.mo_id.move_raw_ids.filtered(
            lambda l: l.state == 'draft')._action_confirm()
        return res
