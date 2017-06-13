# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models, _
from openerp.exceptions import UserError


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_auto_procurement_group_data(self, procurement):
        name = self.env['ir.sequence'].next_by_code(
            'procurement.group') or False
        if not name:
            raise UserError(_('No sequence defined for procurement group'))
        return {
            'name': name
        }

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)

        if (procurement.rule_id and not procurement.group_id and
                procurement.rule_id.auto_create_group):
            group_data = self._prepare_auto_procurement_group_data(procurement)
            group = self.env['procurement.group'].create(group_data)
            procurement.group_id = group
        return res
