# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    removal_priority = fields.Integer(
        related='location_id.removal_priority', readonly=True, store=True)

    @api.model
    def apply_removal_strategy(self, quantity, move, ops=False,
                               domain=None, removal_strategy='fifo'):
        if any(move.mapped('location_id.removal_priority')):
            if removal_strategy == 'fifo':
                order = 'in_date, removal_priority, id'
                return self._quants_get_order(
                    quantity, move, ops=ops, domain=domain, orderby=order)
            elif removal_strategy == 'lifo':
                order = 'in_date desc, removal_priority asc, id desc'
                return self._quants_get_order(
                    quantity, move, ops=ops, domain=domain, orderby=order)
            raise UserError(_('Removal strategy %s not implemented.') % (
                removal_strategy,))
        else:
            return super(StockQuant, self).apply_removal_strategy(
                self, quantity, move, ops=ops, domain=domain,
                removal_strategy=removal_strategy)
