# -*- coding: utf-8 -*-
# © 2015 OdooMRP team
# © 2015 AvanzOSC
# © 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _mergeable_domain(self):
        """Return the quants which may be merged with the current record"""
        self.ensure_one()
        return [('id', '!=', self.id),
                ('product_id', '=', self.product_id.id),
                ('lot_id', '=', self.lot_id.id),
                ('package_id', '=', self.package_id.id),
                ('location_id', '=', self.location_id.id),
                ('reservation_id', '=', False),
                ('propagated_from_id', '=', self.propagated_from_id.id)]

    @api.multi
    def merge_stock_quants(self):
        pending_quants = self.filtered(lambda x: True)
        for quant2merge in self:
            if (quant2merge in pending_quants and
                    not quant2merge.reservation_id):
                quants = self.search(self._mergeable_domain())
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
