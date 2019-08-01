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


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    state = fields.Selection(selection=REQUEST_STATES, string='Status',
                             copy=False, default='draft', index=True,
                             readonly=True, track_visibility='onchange',
                             )

    @api.multi
    def action_submit(self):
        for line in self.stock_request_ids:
            line.action_submit()
        self.state = 'submitted'
        return True
