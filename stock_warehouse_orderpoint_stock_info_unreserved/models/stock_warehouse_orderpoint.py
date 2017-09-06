# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from collections import defaultdict


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.multi
    def _compute_product_available_qty(self):
        super(StockWarehouseOrderpoint, self)._compute_product_available_qty()
        op_by_loc = defaultdict(lambda: self.env['stock.warehouse.orderpoint'])
        for order in self:
            op_by_loc[order.location_id] |= order
        for location_id, order_in_loc in op_by_loc.items():
            products = order_in_loc.mapped('product_id').with_context(
                location=location_id.id)._compute_qty_available_not_res()
            for order in order_in_loc:
                product = products[order.product_id.id]
                order.product_location_qty_available_not_res = \
                    product['qty_available_not_res']

    product_location_qty_available_not_res = fields.Float(
        string='Quantity On Location (Unreserved)',
        compute='_compute_product_available_qty')
