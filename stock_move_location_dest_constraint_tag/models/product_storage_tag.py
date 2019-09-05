# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class ProductStorageTag(models.Model):

    _name = 'product.storage.tag'
    _description = 'Storage tag'

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
