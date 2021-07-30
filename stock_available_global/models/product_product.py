# Copyright 2016-2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = ['product.product', 'product.stock.available.mixin']
    _name = 'product.product'

    def open_stock_avaliable_global(self):
        action = self.sudo().env.ref('stock.product_open_quants').read()[0]
        return action
