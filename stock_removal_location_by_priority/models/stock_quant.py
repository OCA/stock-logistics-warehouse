# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError


class Quant(models.Model):
    _inherit = 'stock.quant'

    removal_priority = fields.Integer(
        related='location_id.removal_priority', readonly=True, store=True)

    @api.model
    def _quants_removal_get_order(self, removal_strategy=None):
        if self.user_has_groups(
                'stock_removal_location_by_priority.group_removal_priority'):
            if removal_strategy == 'fifo':
                return 'in_date, removal_priority, id'
            elif removal_strategy == 'lifo':
                return 'in_date desc, removal_priority asc, id desc'
            raise UserError(_('Removal strategy %s not implemented.') % (
                removal_strategy,))
        else:
            return super(Quant, self)._quants_removal_get_order(
                removal_strategy=removal_strategy)
