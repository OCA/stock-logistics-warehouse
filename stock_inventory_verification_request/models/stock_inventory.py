# Copyright 2017-20 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    solving_slot_verification_request_id = fields.Many2one(
        comodel_name="stock.slot.verification.request",
        help="This Inventory adjustment was created from the specified SVR.",
    )


class StockQuant(models.Model):
    _inherit = "stock.quant"
    _rec_name = "product_id"

    slot_verification_ids = fields.One2many(
        comodel_name="stock.slot.verification.request",
        inverse_name="quant_id",
        string="Slot Verification Request",
    )
    requested_verification = fields.Boolean(
        string="Requested Verification?", copy=False
    )
    allow_svr_creation = fields.Boolean(
        string="Allow SVR Creation",
        compute="_compute_allow_svr_creation",
    )

    @api.model
    def _get_inventory_fields_create(self):
        fields = super()._get_inventory_fields_create()
        fields.extend(["slot_verification_ids", "requested_verification"])
        return fields

    @api.depends("discrepancy_percent", "discrepancy_threshold")
    def _compute_allow_svr_creation(self):
        for record in self:
            record.allow_svr_creation = (
                record.discrepancy_percent > record.discrepancy_threshold
            )

    def action_open_svr(self):
        """Open the corresponding Slot Verification Request directly from the
        stock quant."""
        request_svr_ids = self.mapped("slot_verification_ids").ids
        xmlid = "stock_inventory_verification_request.action_slot_verification_request"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if len(request_svr_ids) > 1:
            action["domain"] = [("id", "in", request_svr_ids)]
        elif len(request_svr_ids) == 1:
            view = self.env.ref(
                "stock_inventory_verification_request.stock_"
                "slot_verification_request_form_view",
                False,
            )
            action["views"] = [(view and view.id or False, "form")]
            action["res_id"] = request_svr_ids[0] or False
        return action

    def action_request_verification(self):
        for quant in self:
            if quant.discrepancy_threshold and (
                quant.discrepancy_percent > quant.discrepancy_threshold
            ):
                self.env["stock.slot.verification.request"].create(
                    {
                        "quant_id": quant.id,
                        "location_id": quant.location_id.id,
                        "state": "wait",
                        "product_id": quant.product_id.id,
                        "company_id": quant.company_id.id,
                        "lot_id": quant.lot_id.id if quant.lot_id else False,
                    }
                )
                quant.requested_verification = True
        return {"type": "ir.actions.act_window_close"}
