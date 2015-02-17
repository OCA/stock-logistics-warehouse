# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.one
    def _product_available_qty(self):
        self.product_location_qty = self.product_id.with_context(
            location=self.location_id.id
            )._product_available()[self.product_id.id]['qty_available']

    @api.one
    @api.depends('product_location_qty', 'product_min_qty')
    def _product_available(self):
        self.available = self.product_location_qty > self.product_min_qty

    product_location_qty = fields.Float(
        string='Quantity On Location', compute='_product_available_qty')
    available = fields.Boolean(
        string='Is enough product available?', compute='_product_available',
        store=True)
