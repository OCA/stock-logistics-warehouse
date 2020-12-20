# Copyright 2020 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    stock_request_ids = fields.One2many("stock.request", "lead_id", string="Requests")
    stock_request_count = fields.Integer(compute="_compute_stock_request_count")

    @api.depends("stock_request_ids")
    def _compute_stock_request_count(self):
        for rec in self:
            count = 0
            if rec.stock_request_ids:
                count = len(rec.stock_request_ids)
            self.stock_request_count = count

    def create_stock_request(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(
                _("You need to define the customer to make a stock request.")
            )
        return {
            "name": _("Stock Requests"),
            "type": "ir.actions.act_window",
            "res_model": "stock.request",
            "target": "current",
            "view_mode": "form",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_lead_id": self.id,
            },
        }

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = (
            self.sudo().env.ref("stock_request.action_stock_request_form").read()[0]
        )

        requests = self.mapped("stock_request_ids")
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action
