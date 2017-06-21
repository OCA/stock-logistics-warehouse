# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockInventoryRevaluationGetQuants(models.TransientModel):

    _name = 'stock.inventory.revaluation.get.quant'
    _description = 'Inventory revaluation get Quants'

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

    def _select_quants(self, revaluation):
        quant_l = []
        quant_obj = self.env['stock.quant']
        for prod_variant in \
                revaluation.product_id:
            search_domain = self._get_quant_search_criteria(prod_variant)
            quants = quant_obj.search(search_domain)
            for quant in quants:
                quant_l.append(quant)
        return quant_l

    def _prepare_line_quant_data(self, revaluation, quant):
        return {
            'revaluation_id': revaluation.id,
            'quant_id': quant.id,
            'new_cost': quant.cost
        }

    @api.multi
    def process(self):
        self.ensure_one()
        if self.env.context.get('active_id', False):
            reval_obj = self.env['stock.inventory.revaluation']
            reval_quant_obj = self.env['stock.inventory.revaluation.quant']
            revaluation = reval_obj.browse(self.env.context['active_id'])
            # Delete the previous records
            for reval_quant in revaluation.reval_quant_ids:
                reval_quant.unlink()

            quants = self._select_quants(revaluation)
            for q in quants:
                q_data = self._prepare_line_quant_data(revaluation, q)
                reval_quant_obj.create(q_data)

        return {'type': 'ir.actions.act_window_close'}
