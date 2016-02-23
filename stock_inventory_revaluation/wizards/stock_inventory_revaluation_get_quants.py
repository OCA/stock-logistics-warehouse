# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class StockInventoryRevaluationGetQuants(models.TransientModel):

    _name = 'stock.inventory.revaluation.line.get.quant'
    _description = 'Inventory revaluation line get Quants'

    date_from = fields.Date('Date From')

    date_to = fields.Date('Date To')

    def _get_quant_search_criteria(self, product_variant):
        domain = [('product_id', '=', product_variant.id),
                  ('location_id.usage', '=', 'internal')]
        if self.date_from:
            domain.extend([('in_date', '>=', self.date_from)])
        if self.date_to:
            domain.extend([('in_date', '<=', self.date_to)])

        return domain

    def _select_quants(self, line):
        quant_l = []
        quant_obj = self.env['stock.quant']
        for prod_variant in line.product_template_id.product_variant_ids:
            search_domain = self._get_quant_search_criteria(prod_variant)
            quants = quant_obj.search(search_domain)
            for quant in quants:
                quant_l.append(quant)
        return quant_l

    def _prepare_line_quant_data(self, line, quant):
        return {
            'line_id': line.id,
            'quant_id': quant.id,
            'new_cost': quant.cost
        }

    @api.one
    def process(self):
        if self.env.context.get('active_id', False):
            line_obj = self.env['stock.inventory.revaluation.line']
            line_quant_obj = self.env['stock.inventory.revaluation.line.quant']
            line = line_obj.browse(self.env.context['active_id'])
            # Delete the previous records
            for line_quant in line.line_quant_ids:
                line_quant.unlink()

            quants = self._select_quants(line)
            for q in quants:
                q_data = self._prepare_line_quant_data(line, q)
                line_quant_obj.create(q_data)

        return {'type': 'ir.actions.act_window_close'}
