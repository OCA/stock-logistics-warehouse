# Copyright 2020 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    partner_id = fields.Many2one(
        "res.partner", states={"draft": [("readonly", False)]}, readonly=True
    )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.stock_request_ids.update(
                {
                    "partner_id": self.partner_id,
                }
            )
