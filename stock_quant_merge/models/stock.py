# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def merge_stock_quants(self):
        pending_quants = self.filtered(lambda x: True)
        for quant2merge in self:
            if (quant2merge in pending_quants and
                    not quant2merge.reservation_id):
                quants = self.search(
                    [('id', '!=', quant2merge.id),
                     ('product_id', '=', quant2merge.product_id.id),
                     ('lot_id', '=', quant2merge.lot_id.id),
                     ('package_id', '=', quant2merge.package_id.id),
                     ('location_id', '=', quant2merge.location_id.id),
                     ('reservation_id', '=', False),
                     ('propagated_from_id', '=',
                      quant2merge.propagated_from_id.id)])
                cont = 1
                cost = quant2merge.cost
                for quant in quants:
                    if (self._get_latest_move(quant2merge) ==
                            self._get_latest_move(quant)):
                        quant2merge.sudo().qty += quant.qty
                        cost += quant.cost
                        cont += 1
                        pending_quants -= quant
                        quant.sudo().unlink()
                quant2merge.sudo().cost = cost / cont

    @api.model
    def quants_unreserve(self, move):
        quants = move.reserved_quant_ids
        super(StockQuant, self).quants_unreserve(move)
        quants.merge_stock_quants()
