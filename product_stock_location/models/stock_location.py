# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.multi
    def write(self, vals):
        res = super(StockLocation, self).write(vals)
        if vals.get('location_id', False):
            for rec in self:
                psts = self.env['product.stock.location'].search(
                    [('location_id', '=', rec.location_id.id)])
                for pst in psts:
                    parent_psts = self.env['product.stock.location'].search(
                        [('product_id', '=', pst.product_id.id),
                         ('location_id', '=', vals['location_id'])], limit=1)
                    if parent_psts:
                        pst.write({'parent_id': parent_psts[0]})
        return res
