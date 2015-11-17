# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, exceptions
from openerp.tools.safe_eval import safe_eval


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.multi
    def action_traceability(self):
        """Replace the action on stock moves with an action on the report"""
        action = super(StockProductionLot, self).action_traceability()
        if action['res_model'] != 'stock.move':
            raise exceptions.ValidationError(
                "An incompatible module returned an action for the wrong "
                "model.")
        moves = self.env['stock.move'].search(safe_eval(action['domain']))
        return moves.mapped('quant_ids').action_view_quant_history()
