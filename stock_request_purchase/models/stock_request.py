# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _inherit = "stock.request"

    purchase_ids = fields.One2many(
        "purchase.order",
        compute="_compute_purchase_ids",
        string="Purchase Orders",
        readonly=True,
    )
    purchase_count = fields.Integer(compute="_compute_purchase_ids", readonly=True)
    purchase_line_ids = fields.Many2many(
        "purchase.order.line", string="Purchase Order Lines", readonly=True, copy=False
    )

    @api.depends("purchase_line_ids")
    def _compute_purchase_ids(self):
        for request in self:
            request.purchase_ids = request.purchase_line_ids.mapped("order_id")
            request.purchase_count = len(request.purchase_ids)

    @api.constrains("purchase_line_ids", "company_id")
    def _check_purchase_company_constrains(self):
        if any(
            any(line.company_id != req.company_id for line in req.purchase_line_ids)
            for req in self
        ):
            raise ValidationError(
                _(
                    "You have linked to a purchase order line "
                    "that belongs to another company."
                )
            )

    def action_view_purchase(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("purchase.purchase_rfq")

        purchases = self.mapped("purchase_ids")
        if len(purchases) > 1:
            action["domain"] = [("id", "in", purchases.ids)]
        elif purchases:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = purchases.id
        return action
