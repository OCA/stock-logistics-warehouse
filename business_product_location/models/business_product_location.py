# -*- coding: utf-8 -*-
# Copyright 2015-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BusinessProductLocation(models.Model):
    _name = 'business.product.location'

    name = fields.Char(
        required=True
    )
    product_ids = fields.One2many(
        'business.product.line',
        'business_product_location_id',
        string='Products'
    )
    location_ids = fields.One2many(
        'stock.location',
        'business_usage_id',
        string='Locations'
    )
