# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, _
from odoo.exceptions import UserError


class StockInventoryRevaluationMassPost(models.TransientModel):

    _name = 'stock.inventory.revaluation.mass.post'
    _description = 'Post multiple inventory revaluations'

    @api.multi
    def process(self):
        active_model = self.env.context['active_model']
        assert active_model == 'stock.inventory.revaluation', \
            'Bad context propagation'
        self.ensure_one()
        revaluation_ids = self.env.context.get('active_ids', [])
        revaluation_obj = self.env['stock.inventory.revaluation']
        for revaluation in revaluation_obj.browse(revaluation_ids):
            if revaluation.state != 'draft':
                raise UserError(
                    _('Revaluation %s is not in Draft state') %
                    revaluation.name)
            revaluation.button_post()

        return {'type': 'ir.actions.act_window_close'}
