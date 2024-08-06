# Copyright 2017-20 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    slot_verification_ids = fields.One2many(
        comodel_name="stock.slot.verification.request",
        string="Slot Verification Requests", inverse_name="location_id")

    @api.multi
    def action_open_svr(self):
        """Open the corresponding Slot Verification Request directly from the
        Location."""
        request_svr_ids = self.mapped("slot_verification_ids").ids
        action = self.env.ref("stock_inventory_verification_request."
                              "action_slot_verification_request")
        result = action.read()[0]
        if len(request_svr_ids) > 1:
            result["domain"] = [("id", "in", request_svr_ids)]
        elif len(request_svr_ids) == 1:
            view = self.env.ref(
                "stock_inventory_verification_request.stock_"
                "slot_verification_request_form_view", False)
            result["views"] = [(view and view.id or False, "form")]
            result["res_id"] = request_svr_ids[0] or False
        return result
