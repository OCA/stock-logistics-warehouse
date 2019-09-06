# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class ProductProduct(models.Model):

    _inherit = 'product.product'

    abc_putaway_strategy_ids = fields.One2many(
        'stock.abc.putaway.strat',
        'product_id',
        string="Product ABC Put-aways",
    )
    category_abc_putaway_ids = fields.One2many(
        related='categ_id.abc_putaway_strategy_ids',
        string="Category ABC Put-aways",
    )
