# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models, _, exceptions


class StockInventoryRevaluationMassPost(models.TransientModel):

    _name = 'stock.inventory.revaluation.mass.post'
    _description = 'Post multiple inventory revaluations'

    @api.model
    def default_get(self, fields):
        res = super(StockInventoryRevaluationMassPost, self).default_get(
            fields)
        revaluation_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']

        if not revaluation_ids:
            return res
        assert active_model == 'stock.inventory.revaluation', \
            'Bad context propagation'
        return res

    @api.multi
    def process(self):
        self.ensure_one()
        revaluation_ids = self.env.context.get('active_ids', [])
        revaluation_obj = self.env['stock.inventory.revaluation']
        for revaluation in revaluation_obj.browse(revaluation_ids):
            if revaluation.state != 'draft':
                raise exceptions.Warning(
                    _('Revaluation %s is not in Draft state') %
                    revaluation.name)
            revaluation.button_post()

        return {'type': 'ir.actions.act_window_close'}
