# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    stock_request_id = fields.Many2one('stock.request', readonly=True)

    def _get_stock_move_values(self):
        result = super(ProcurementOrder, self)._get_stock_move_values()
        if self.stock_request_id:
            result['allocation_ids'] = [(0, 0, {
                'stock_request_id': self.stock_request_id.id,
                'requested_product_uom_qty': self.product_qty,
            })]
        return result
