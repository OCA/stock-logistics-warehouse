# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRequestOrder(models.Model):

    _inherit = "stock.request.order"

    purchase_request_ids = fields.One2many(
        "purchase.request",
        compute="_compute_purchase_request_ids",
        string="Purchase Requests",
        readonly=True,
    )
    purchase_request_count = fields.Integer(
        compute="_compute_purchase_request_ids", readonly=True
    )
    purchase_request_line_ids = fields.Many2many(
        "purchase.request.line",
        string="Purchase Request Lines",
        readonly=True,
        copy=False,
    )

    @api.depends("stock_request_ids")
    def _compute_purchase_request_ids(self):
        for req in self:
            req.purchase_request_ids = req.stock_request_ids.mapped(
                "purchase_request_ids"
            )
            req.purchase_request_line_ids = req.stock_request_ids.mapped(
                "purchase_request_line_ids"
            )
            req.purchase_request_count = len(req.purchase_request_ids)

    def action_view_purchase_request(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase_request.purchase_request_form_action"
        )
        purchase_requests = self.mapped("purchase_request_ids")
        if len(purchase_requests) > 1:
            action["domain"] = [("id", "in", purchase_requests.ids)]
            action["views"] = [
                (
                    self.env.ref("purchase_request.view_purchase_request_tree").id,
                    "tree",
                ),
                (
                    self.env.ref("purchase_request.view_purchase_request_form").id,
                    "form",
                ),
            ]
        elif purchase_requests:
            action["views"] = [
                (self.env.ref("purchase_request.view_purchase_request_form").id, "form")
            ]
            action["res_id"] = purchase_requests.id
        return action
