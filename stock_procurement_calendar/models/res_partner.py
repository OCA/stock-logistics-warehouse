# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict
from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    procurement_calendar_count = fields.Integer(
        compute='_compute_procurement_calendar_count'
    )

    @api.multi
    def _get_procurement_calendar_domain(self):
        return [
            ('partner_id', 'in', self.ids)
        ]

    @api.multi
    def _compute_procurement_calendar_count(self):
        count_list = defaultdict()
        read_counts = self.env['procurement.calendar'].read_group(
            self._get_procurement_calendar_domain(),
            ['partner_id'], ['partner_id']
        )
        for read_count in read_counts:
            count_list[read_count['partner_id'][0]] =\
                read_count['partner_id_count']
        for partner in self:
            partner.procurement_calendar_count = count_list.get(partner.id, 0)
