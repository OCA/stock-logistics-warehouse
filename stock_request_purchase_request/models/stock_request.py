# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequest(models.Model):

    _inherit = "stock.request"

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

    @api.depends("purchase_line_ids")
    def _compute_purchase_request_ids(self):
        for request in self:
            request.purchase_request_ids = request.purchase_request_line_ids.mapped(
                "request_id"
            )
            request.purchase_request_count = len(request.purchase_request_ids)

    @api.constrains("purchase_request_line_ids", "company_id")
    def _check_purchase_request_company_constrains(self):
        if any(
            any(
                line.company_id != req.company_id
                for line in req.purchase_request_line_ids
            )
            for req in self
        ):
            raise ValidationError(
                _(
                    "You have linked to a purchase request line "
                    "that belongs to another company."
                )
            )

    def action_cancel(self):
        """Propagate the cancellation to the generated purchase request."""
        res = super().action_cancel()
        for record in self:
            record.sudo().purchase_request_ids.filtered(
                lambda x: x.state not in ("done", "rejected")
                and x.stock_request_ids == record
            ).button_rejected()
        return res

    def action_view_purchase_request(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase_request.purchase_request_form_action"
        )

        purchase_requests = self.mapped("purchase_request_ids")
        if len(purchase_requests) > 1:
            action["domain"] = [("id", "in", purchase_requests.ids)]
        elif purchase_requests:
            action["views"] = [
                (self.env.ref("purchase_request.view_purchase_request_form").id, "form")
            ]
            action["res_id"] = purchase_requests.id
        return action
