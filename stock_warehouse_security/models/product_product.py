# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_view_stock_move_lines(self):
        action = super().action_view_stock_move_lines()
        wh_id = self.env.user.warehouse_id.id
        action['context']['search_default_warehouse_id'] = wh_id
        return action

    # Be aware that the exact same function exists in product.template
    def action_open_quants(self):
        action = super().action_open_quants()
        wh_id = self.env.user.warehouse_id.id
        action['context']['search_default_warehouse_id'] = wh_id
        return action
