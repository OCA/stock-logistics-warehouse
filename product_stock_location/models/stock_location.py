# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.model
    def prepare_product_stock_location_data(self, product, location):
        parent = self.env['product.stock.location']
        if location.location_id:
            parent = self.env['product.stock.location'].search(
                [('product_id', '=', product.id),
                 ('location_id', '=', location.location_id.id)])

        return {
            'product_id': product.id,
            'location_id': location.id,
            'parent_id': parent.id or False,
        }

    @api.model
    def update_product_stock_location(self, vals):
        pst_model = self.env['product.stock.location']
        psts = self.env['product.stock.location'].search(
            [('location_id', '=', self.id)])
        for pst in psts:
            parent_psts = self.env['product.stock.location'].search(
                [('product_id', '=', pst.product_id.id),
                 ('location_id', '=', self.location_id.id)], limit=1)
            if parent_psts:
                pst.parent_id = parent_psts[0]
            else:
                new_pst = pst_model.create(
                    self.prepare_product_stock_location_data(
                        pst.product_id, self.location_id))
                pst.parent_id = new_pst

    @api.multi
    def write(self, vals):
        res = super(StockLocation, self).write(vals)
        if vals.get('location_id', False):
            self._parent_store_compute()
        if vals.get('location_id', False):
            for rec in self:
                rec.sudo().update_product_stock_location(vals)
        return res
