# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def quants_unreserve(self):
        for move in self:
            quants = move.reserved_quant_ids
            super(StockMove, move).quants_unreserve()
            if (
                    quants and
                    not self.env.context.get('disable_stock_quant_merge')):
                quants.merge_stock_quants()
