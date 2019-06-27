# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    removal_priority = fields.Integer(
        related='location_id.removal_priority',
        store=True,
    )

    @api.model
    def _get_removal_strategy_order(self, removal_strategy=None):
        if self.user_has_groups(
                'stock_removal_location_by_priority.group_removal_priority'):
            if removal_strategy == 'fifo':
                return 'in_date ASC NULLS FIRST, removal_priority ASC, id'
            elif removal_strategy == 'lifo':
                return 'in_date DESC NULLS LAST, removal_priority ASC, id desc'
            raise UserError(_('Removal strategy %s not implemented.') % (
                removal_strategy,))
        else:
            return super()._get_removal_strategy_order(
                removal_strategy=removal_strategy)
