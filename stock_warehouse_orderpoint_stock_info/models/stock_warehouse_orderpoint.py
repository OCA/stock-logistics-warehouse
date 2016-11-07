# -*- coding: utf-8 -*-
# Copyright 2016 OdooMRP Team
# Copyright 2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.one
    def _product_available_qty(self):
        product_available = self.product_id.with_context(
            location=self.location_id.id
            )._product_available()[self.product_id.id]
        self.product_location_qty = product_available['qty_available']
        self.incoming_location_qty = product_available['incoming_qty']
        self.outgoing_location_qty = product_available['outgoing_qty']
        self.virtual_location_qty = product_available['virtual_available']

    @api.one
    @api.depends('product_location_qty', 'product_min_qty')
    def _product_available(self):
        self.available = self.product_location_qty > self.product_min_qty

    product_location_qty = fields.Float(
        string='Quantity On Location', compute='_product_available_qty')
    incoming_location_qty = fields.Float(
        string='Incoming On Location', compute='_product_available_qty')
    outgoing_location_qty = fields.Float(
        string='Outgoing On Location', compute='_product_available_qty')
    virtual_location_qty = fields.Float(
        string='Forecast On Location', compute='_product_available_qty')

    available = fields.Boolean(
        string='Is enough product available?', compute='_product_available',
        store=True)
    product_category = fields.Many2one(string='Product Category',
                                       related='product_id.categ_id',
                                       store=True)
