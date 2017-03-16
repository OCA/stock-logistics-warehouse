# -*- coding: utf-8 -*-
# © 2015 OdooMRP team
# © 2015 AvanzOSC
# © 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


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
        # Get a copy of the recorset
        pending_quants = self.browse(self.ids)
        for quant2merge in self.filtered(lambda x: not x.reservation_id):
            if quant2merge in pending_quants:
                quants = self.search(quant2merge._mergeable_domain())
                cont = 1
                cost = quant2merge.cost
                for quant in quants:
                    if (quant2merge._get_latest_move() ==
                            quant._get_latest_move()):
                        quant2merge.sudo().qty += quant.qty
                        cost += quant.cost
                        cont += 1
                        pending_quants -= quant
                        quant.with_context(force_unlink=True).sudo().unlink()
                quant2merge.sudo().cost = cost / cont
