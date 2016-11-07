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

    @api.multi
    def _compute_product_available_qty(self):
        for rec in self:
            product_available = rec.product_id.with_context(
                location=rec.location_id.id
                )._product_available()[rec.product_id.id]
            rec.product_location_qty = product_available['qty_available']
            rec.incoming_location_qty = product_available['incoming_qty']
            rec.outgoing_location_qty = product_available['outgoing_qty']
            rec.virtual_location_qty = product_available['virtual_available']

    product_location_qty = fields.Float(
        string='Quantity On Location',
        compute='_compute_product_available_qty')
    incoming_location_qty = fields.Float(
        string='Incoming On Location',
        compute='_compute_product_available_qty')
    outgoing_location_qty = fields.Float(
        string='Outgoing On Location',
        compute='_compute_product_available_qty')
    virtual_location_qty = fields.Float(
        string='Forecast On Location',
        compute='_compute_product_available_qty')
    product_category = fields.Many2one(string='Product Category',
                                       related='product_id.categ_id',
                                       store=True)
