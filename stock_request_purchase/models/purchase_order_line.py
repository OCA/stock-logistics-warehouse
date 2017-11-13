# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    stock_request_ids = fields.Many2many(comodel_name='stock.request',
                                         string='Stock Requests', copy=False)

    @api.multi
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)

        for re in res:
            re['allocation_ids'] = [
                (0, 0, {
                    'stock_request_id': request.id,
                    'requested_product_uom_qty': request.product_qty,
                }) for request in self.stock_request_ids]
        return res
