# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    auto_create_group = fields.Boolean(string='Auto-create Procurement Group')
