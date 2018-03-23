# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models
from openerp.tools.float_utils import float_round


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def write(self, values):
        if values.get('type', False):
            new_type = values.get('type')
            if new_type == 'product':
                variants = self.filtered(lambda r: r.type == 'consu').mapped(
                    'product_variant_ids')
                if variants:
                    self.env['stock.quant'].search(
                        [('product_id', 'in', variants.ids)]).sudo().write(
                        {'cost': 0.0})
                    variants.standard_price = 0.0
        if values.get('cost_method', False):
            new_method = values.get('cost_method')
            product_type = values.get('type', False)
            self.update_cost_method(new_method, product_type)
        return super(ProductTemplate, self).write(values)

    @api.multi
    def update_cost_method(self, new_method, product_type):
        if new_method == 'real':
            variants = self.filtered(
                lambda r: product_type == 'product' or
                r.type == 'product').mapped(
                    'product_variant_ids')
            for rec in variants:
                quants = self.env['stock.quant'].search(
                    [('product_id', '=', rec.product_variant_ids.id),
                     ('location_id.usage', '=', 'internal')])
                quants.sudo().write(
                    {'cost': rec.standard_price})
        elif new_method != 'real':
            for variant in self.filtered(lambda r: r.cost_method == 'real'):
                total_cost = 0.0
                total_qty = 0.0
                rounding = variant.uom_id.rounding
                for variant in variant.product_variant_ids:
                    quants = self.env['stock.quant'].search(
                        [('product_id', '=', variant.id),
                         ('location_id.usage', '=', 'internal')])

                    for quant in quants:
                        total_cost += quant.cost * quant.qty
                        total_qty += quant.qty
                if total_qty:
                    avg_cost = total_cost / total_qty
                else:
                    avg_cost = 0.0
                variant.standard_price = float_round(
                    avg_cost, precision_rounding=rounding)
        return True
