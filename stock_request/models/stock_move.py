# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    allocation_ids = fields.One2many(comodel_name='stock.request.allocation',
                                     inverse_name='stock_move_id',
                                     string='Stock Request Allocation')

    stock_request_ids = fields.One2many(comodel_name='stock.request',
                                        string='Stock Requests',
                                        compute='_compute_stock_request_ids')

    @api.depends('allocation_ids')
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_ids = rec.allocation_ids.mapped(
                'stock_request_id')

    def _merge_moves_fields(self):
        res = super(StockMove, self)._merge_moves_fields()
        res['allocation_ids'] = [(4, m.id) for m in
                                 self.mapped('allocation_ids')]
        return res
