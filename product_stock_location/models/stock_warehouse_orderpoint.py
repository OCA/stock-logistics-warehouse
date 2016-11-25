# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.multi
    @api.depends('product_stock_location_ids',
                 'product_stock_location_ids.product_location_qty',
                 'product_stock_location_ids.incoming_location_qty',
                 'product_stock_location_ids.outgoing_location_qty',
                 'product_stock_location_ids.virtual_location_qty'
                 )
    def _compute_product_available_qty(self):
        for rec in self:
            for psl in rec.product_stock_location_ids:
                rec.product_location_qty = psl.product_location_qty
                rec.incoming_location_qty = psl.incoming_location_qty
                rec.outgoing_location_qty = psl.outgoing_location_qty
                rec.virtual_location_qty = psl.virtual_location_qty

    product_location_qty = fields.Float(
        string='Quantity On Location',
        compute='_compute_product_available_qty',
        store='True')
    incoming_location_qty = fields.Float(
        string='Incoming On Location',
        compute='_compute_product_available_qty',
        store='True')
    outgoing_location_qty = fields.Float(
        string='Outgoing On Location',
        compute='_compute_product_available_qty',
        store='True')
    virtual_location_qty = fields.Float(
        string='Forecast On Location',
        compute='_compute_product_available_qty',
        store='True')
    product_category = fields.Many2one(string='Product Category',
                                       related='product_id.categ_id',
                                       store=True)
    product_stock_location_ids = fields.One2many(
        comodel_name='product.stock.location', inverse_name='orderpoint_id',
        string='Product Stock Locations')
