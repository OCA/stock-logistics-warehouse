# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class ProductCategory(models.Model):

    _inherit = 'product.category'

    product_storage_tag_ids = fields.Many2many(
        'product.storage.tag',
        string='Storage Tags',
    )
