# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockRequest(models.Model):
    _name = "stock.request.order"
    _inherit = ['stock.request.order', 'tier.validation']
    _state_from = ['draft']
    _state_to = ['open']

    @api.model
    def _get_under_validation_exceptions(self):
        res = super(StockRequest, self)._get_under_validation_exceptions()
        res.append('route_id')
        return res
