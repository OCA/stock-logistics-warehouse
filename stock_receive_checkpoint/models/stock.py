# -*- coding: utf-8 -*-
# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    ordered_qty = fields.Float(related="purchase_line_id.product_qty")
    received_date = fields.Date(compute="_compute_received_and_diff")
    diff_qty = fields.Float(compute="_compute_received_and_diff")
    visual_flag = fields.Char(compute="_compute_visual_flag")

    def _compute_received_and_diff(self):
        date_by_purch = {
            x.purchase_line_id: x.date
            for x in self.search(
                [
                    ("purchase_line_id", "in", self.mapped("purchase_line_id").ids),
                    ("state", "=", "done"),
                ],
                order="date ASC",
            )
        }
        for rec in self:
            if rec.purchase_line_id in date_by_purch:
                rec.received_date = date_by_purch[rec.purchase_line_id]
            rec.diff_qty = rec.ordered_qty - rec.product_qty

    @api.depends("diff_qty")
    def _compute_visual_flag(self):
        ctx_date = self.env.context.get("date") or fields.Date.today()
        for rec in self:
            if not rec.received_date and rec.date_expected < ctx_date:
                rec.visual_flag = "toreceive"
            elif rec.diff_qty < 0 and rec.date_expected < ctx_date:
                rec.visual_flag = "inlate"
            elif rec.diff_qty > 0 and rec.date_expected < ctx_date:
                rec.visual_flag = "more"
