# Copyright 2019 Open Source Integrators
# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models, _


class StockRequest(models.Model):
    _inherit = 'stock.request'

    def __get_request_states(self):
        states = super().__get_request_states()
        if not ('submitted', _('Submitted')) in states:
            states.insert(
                states.index(('draft', _('Draft'))) + 1,
                ('submitted', _('Submitted')))
        return states

    route_id = fields.Many2one(states={'draft': [('readonly', False)],
                                       'submitted': [('readonly', False)]})

    @api.multi
    def action_submit(self):
        self._action_submit()

    @api.multi
    def _action_submit(self):
        self.state = 'submitted'

    def _skip_procurement(self):
        return super(StockRequest, self)._skip_procurement() and \
            self.state != 'submitted' or \
            self.product_id.type not in ('consu', 'product')
