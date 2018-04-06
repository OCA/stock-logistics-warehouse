# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _mergeable_domain(self):
        domain = super(StockQuant, self)._mergeable_domain()

        if self.product_id.cost_method == 'real':
            domain += [('cost', '=', self.cost),
                       ('in_date', '=', self.in_date)]

        return domain
