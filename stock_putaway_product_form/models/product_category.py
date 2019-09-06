# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class ProductCategory(models.Model):

    _inherit = 'product.category'

    fixed_putaway_strategy_ids = fields.One2many(
        'stock.fixed.putaway.strat', 'category_id', string="Fixed Put-aways",
    )
