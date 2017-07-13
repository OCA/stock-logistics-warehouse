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
                        [('product_id', 'in', variants.ids)]).write(
                        {'cost': 0.0})
                    variants.standard_price = 0.0

        if values.get('cost_method', False):
            new_method = values.get('cost_method')
            if new_method == 'real':
                variants = self.filtered(lambda r: values.get(
                    'type', False) == 'product' or r.type == 'product').mapped(
                    'product_variant_ids')
                for variant in variants:
                    self.env['stock.quant'].search(
                        [('product_id', 'in', variants.ids),
                         ('location_id.usage', '=', 'internal')]).write(
                        {'cost': variant.standard_price})
            elif new_method != 'real':
                variants = self.filtered(lambda r: r.cost_method == 'real').\
                    mapped('product_variant_ids')
                for variant in variants:
                    total_cost = 0.0
                    total_qty = 0.0
                    rounding = variant.uom_id.rounding
                    for quant in self.env['stock.quant'].search(
                            [('product_id', '=', variant.id),
                             ('location_id.usage', '=', 'internal')]):
                        total_cost += quant.cost * quant.qty
                        total_qty += quant.qty
                    if total_qty:
                        avg_cost = total_cost / total_qty
                    else:
                        avg_cost = 0.0
                    variant.standard_price = \
                        float_round(avg_cost, precision_rounding=rounding)

        return super(ProductTemplate, self).write(values)
