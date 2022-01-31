# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    stock_request_ids = fields.One2many(
        comodel_name="stock.request",
        inverse_name="analytic_account_id",
        string="Stock Requests",
        copy=False,
    )

    def action_view_stock_request(self):
        self.ensure_one()
        xmlid = "stock_request.action_stock_request_form"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        requests = self.mapped("stock_request_ids")
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action
