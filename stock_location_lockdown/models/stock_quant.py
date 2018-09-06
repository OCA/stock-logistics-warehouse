# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _check_location(self, location):
        res = super(StockQuant, self)._check_location(location)
        if location.block_stock_entrance:
            raise UserError(
                _('The location %s is not configured to receive stock.')
                % (location.name))
        return res
