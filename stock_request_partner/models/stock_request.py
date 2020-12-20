# Copyright 2020 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _inherit = "stock.request"

    partner_id = fields.Many2one(
        "res.partner", states={"draft": [("readonly", False)]}, readonly=True
    )

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id)
        if self.partner_id:
            name = self.name
            if self.order_id:
                name = self.order_id.name
            group = self.env["procurement.group"].search([("name", "=", name)])
            if not group:
                group = self.env["procurement.group"].create(
                    {
                        "name": name,
                        "partner_id": self.partner_id.id,
                        "move_type": self.picking_policy,
                    }
                )
            res["group_id"] = group
        return res

    @api.constrains("order_id", "partner_id")
    def check_order_partner_id(self):
        if self.order_id and self.order_id.partner_id != self.partner_id:
            raise ValidationError(_("Partner must be equal to the order"))
