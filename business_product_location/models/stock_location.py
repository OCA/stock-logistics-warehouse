# -*- coding: utf-8 -*-
# Copyright 2015-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    business_usage_id = fields.Many2one(
        'business.product.location',
        'Business Usage'
    )
