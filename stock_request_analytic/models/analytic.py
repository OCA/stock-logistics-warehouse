# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    stock_request_ids = fields.Many2many(
        "stock.request",
        "stock_request_analytic_rel",
        "analytic_id",
        "request_id",
        string="Stock Requests",
        help="Requests linked through materialized analytic_distribution.",
    )

    def action_view_stock_request(self):
        self.ensure_one()
        orders = self.env["stock.request.order"].search(
            [("stock_request_ids.analytic_account_ids", "in", self.id)]
        )
        action = {
            "name": "Stock Requests",
            "type": "ir.actions.act_window",
            "res_model": "stock.request.order",
            "view_mode": "tree,form",
            "domain": [("id", "in", orders.ids)],
        }
        if len(orders) == 1:
            action["res_id"] = orders.id
        return action
