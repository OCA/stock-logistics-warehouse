# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.multi
    def _compute_product_available_qty(self):
        super(StockWarehouseOrderpoint, self)._compute_product_available_qty()
        for rec in self:
            product_available = rec.product_id.with_context(
                location=rec.location_id.id
                )._product_available()[rec.product_id.id]
            rec.product_location_qty_available_not_res = \
                product_available['qty_available_not_res']

    product_location_qty_available_not_res = fields.Float(
        string='Quantity On Location (Unreserved)',
        compute='_compute_product_available_qty')
