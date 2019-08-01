# Copyright 2019 Open Source Integrators
# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models

REQUEST_STATES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('open', 'In progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')]


class StockRequest(models.Model):
    _inherit = 'stock.request'

    state = fields.Selection(selection=REQUEST_STATES, string='Status',
                             copy=False, default='draft', index=True,
                             readonly=True, track_visibility='onchange',
                             )
    route_id = fields.Many2one(states={'draft': [('readonly', False)],
                                       'submitted': [('readonly', False)]},
                               readonly=True)

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
