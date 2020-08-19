# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    reason_code_id = fields.Many2one(
        "scrap.reason.code", string="Reason Code", states={"done": [("readonly", True)]}
    )
    scrap_location_id = fields.Many2one(readonly=True)

    def _prepare_move_values(self):
        res = super(StockScrap, self)._prepare_move_values()
        res["reason_code_id"] = self.reason_code_id.id
        return res

    @api.onchange("reason_code_id")
    def _onchange_reason_code_id(self):
        if self.reason_code_id.location_id:
            self.scrap_location_id = self.reason_code_id.location_id

    def write(self, vals):
        if "reason_code_id" in vals:
            location_id = (
                self.env["scrap.reason.code"]
                .browse(vals.get("reason_code_id"))
                .location_id
            )
            if location_id:
                vals.update({"scrap_location_id": location_id})
        return super(StockScrap, self).write(vals)

    @api.model
    def create(self, vals):
        if "reason_code_id" in vals:
            location_id = (
                self.env["scrap.reason.code"]
                .browse(vals.get("reason_code_id"))
                .location_id
            )
            if location_id:
                vals["scrap_location_id"] = location_id.id
        return super(StockScrap, self).create(vals)
