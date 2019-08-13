# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from ast import literal_eval


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_open_quants(self):
        action = super().action_open_quants()
        wh_id = self.env.user.warehouse_id.id
        action['context']['search_default_warehouse_id'] = wh_id
        return action

    def action_view_orderpoints(self):
        action = super().action_view_orderpoints()
        wh_id = self.env.user.warehouse_id.id
        action['context']['search_default_warehouse_id'] = wh_id
        return action

    def action_view_stock_move_lines(self):
        action = super().action_view_stock_move_lines()
        wh_id = self.env.user.warehouse_id.id
        # TODO eval if string? same in product.product
        context = literal_eval(res['context'] or {})
        action['context']['search_default_warehouse_id'] = wh_id
        return action
