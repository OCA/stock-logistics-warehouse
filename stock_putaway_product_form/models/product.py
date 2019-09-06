# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class ProductProduct(models.Model):

    _inherit = 'product.product'

    fixed_putaway_strategy_ids = fields.One2many(
        'stock.fixed.putaway.strat',
        'product_id',
        string="Product Fixed Put-aways"
    )
    category_fixed_putaway_ids = fields.One2many(
        related='categ_id.fixed_putaway_strategy_ids',
        string="Category Fixed Put-aways"
    )
