# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from odoo.tools.translate import _


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    mts_rule_id = fields.Many2one('procurement.rule',
                                  string="MTS Rule")
    mto_rule_id = fields.Many2one('procurement.rule',
                                  string="MTO Rule")

    @api.model
    def _get_action(self):
        return [('split_procurement', _('Choose between MTS and MTO'))] + \
            super(ProcurementRule, self)._get_action()
