# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_auto_procurement_group_data(self):
        name = self.env['ir.sequence'].next_by_code(
            'procurement.group') or False
        if not name:
            raise UserError(_('No sequence defined for procurement group'))
        return {
            'name': name
        }

    @api.multi
    def _assign(self):
        res = super(ProcurementOrder, self)._assign()
        if (self.rule_id and not self.group_id and
                self.rule_id.auto_create_group):
            group_data = self._prepare_auto_procurement_group_data()
            group = self.env['procurement.group'].create(group_data)
            self.group_id = group
        return res
