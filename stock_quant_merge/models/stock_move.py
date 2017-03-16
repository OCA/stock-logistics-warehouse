# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def quants_unreserve(self):
        quants = self.reserved_quant_ids
        super(StockMove, self).quants_unreserve()
        quants.merge_stock_quants()
