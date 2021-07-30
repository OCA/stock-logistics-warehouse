# Copyright 2016-2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = ['product.template', 'product.stock.available.mixin']
    _name = 'product.template'

    def open_stock_forecast_global(self):
        action = self.sudo().env.ref(
            'stock.action_stock_level_forecast_report_template'
        ).read()[0]
        return action
