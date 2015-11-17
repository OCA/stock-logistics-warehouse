# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def action_view_stock_moves(self):
        """Return an action on the report"""
        # We have no super() to call, the standard opens a list of moves
        moves = self.env['stock.move'].search(
            [('product_id', 'in', self.ids)])
        return moves.mapped('quant_ids').action_view_quant_history()
