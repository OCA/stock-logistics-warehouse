# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    purchase_ids = fields.One2many(
        "purchase.order",
        compute="_compute_purchase_ids",
        string="Purchase Orders",
        readonly=True,
    )
    purchase_count = fields.Integer(compute="_compute_purchase_ids", readonly=True)
    purchase_line_ids = fields.Many2many(
        "purchase.order.line",
        compute="_compute_purchase_ids",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )

    @api.depends("stock_request_ids")
    def _compute_purchase_ids(self):
        for req in self:
            req.purchase_ids = req.stock_request_ids.mapped("purchase_ids")
            req.purchase_line_ids = req.stock_request_ids.mapped("purchase_line_ids")
            req.purchase_count = len(req.purchase_ids)

    def action_view_purchase(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("purchase.purchase_rfq")
        purchases = self.mapped("purchase_ids")
        if len(purchases) > 1:
            action["domain"] = [("id", "in", purchases.ids)]
            action["views"] = [
                (self.env.ref("purchase.purchase_order_tree").id, "tree"),
                (self.env.ref("purchase.purchase_order_form").id, "form"),
            ]
        elif purchases:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = purchases.id
        return action
