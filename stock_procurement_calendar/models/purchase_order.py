# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    procurement_calendar_id = fields.Many2one(
        'procurement.calendar'
    )
