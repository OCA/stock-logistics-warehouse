# -*- coding: utf-8 -*-
# Copyright 2015-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    business_usage_ids = fields.One2many(
        'business.product.line',
        'product_id',
        'Business Usage'
    )
