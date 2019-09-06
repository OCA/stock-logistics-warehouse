# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class ProductCategory(models.Model):

    _inherit = 'product.category'

    abc_putaway_strategy_ids = fields.One2many(
        'stock.abc.putaway.strat', 'category_id', string='ABC Put-Aways'
    )
