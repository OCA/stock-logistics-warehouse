# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_stock_location_id = fields.Many2one(
        comodel_name='product.stock.location',
        string="Product Source Stock Location")

    @api.model
    def search_product_stock_location_domain(self, location):
        return [('product_id', '=', self.product_id.id),
                ('location_id', '=', location.id)]

    @api.model
    def prepare_product_stock_location_data(self, location):
        parent = self.env['product.stock.location']
        if location.location_id:
            parent = self.env['product.stock.location'].search(
                [('product_id', '=', self.product_id.id),
                 ('location_id', '=', location.location_id.id)])

        return {
            'product_id': self.product_id.id,
            'location_id': location.id,
            'parent_id': parent.id or False
        }

    @api.model
    def update_product_stock_location(self):
        pst_model = self.env['product.stock.location']
        product_stock_locations = pst_model.search(
            self.search_product_stock_location_domain(self.location_id),
            limit=1)
        if not product_stock_locations:
            pst = pst_model.create(self.prepare_product_stock_location_data(
                self.location_id))
            self.product_stock_location_id = pst
        else:
            self.product_stock_location_id = product_stock_locations[0]

    @api.model
    def create(self, vals):
        quant = super(StockQuant, self).create(vals)
        quant.sudo().update_product_stock_location()

        return quant

    @api.multi
    def write(self, vals):
        res = super(StockQuant, self).write(vals)
        for quant in self:
            if not vals.get('product_stock_location_id', False) and \
                    not vals.get('product_stock_location_dest_id', False):
                quant.sudo().update_product_stock_location()
        return res
