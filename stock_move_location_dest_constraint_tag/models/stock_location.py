# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):

    _inherit = 'stock.location'

    product_storage_tag_ids = fields.Many2many(
        'product.storage.tag',
        string='Storage Tags',
    )

    def check_move_dest_constraint(self, line=None, product=None):
        res = super().check_move_dest_constraint(product)
        if product:
            product_tags = product.product_storage_tag_ids
            if not product_tags:
                product_tags = product.categ_id.product_storage_tag_ids
            if product_tags and not product_tags <= self.product_storage_tag_ids:
                raise ValidationError(_(
                    'Tags mismatch between product tags requirements %s (%s)'
                    ' and location tags allowed %s (%s)' % (
                        product.name,
                        ','.join(product.product_storage_tag_ids.mapped('name')),
                        self.name,
                        ','.join(self.product_storage_tag_ids.mapped('name'))
                    )
                ))
        return res
