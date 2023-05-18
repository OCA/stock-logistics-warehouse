# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    reason_code_id = fields.Many2one(
        comodel_name="scrap.reason.code",
        states={"done": [("readonly", True)]},
        domain="[('id', 'in', allowed_reason_code_ids)]",
    )
    allowed_reason_code_ids = fields.Many2many(
        comodel_name="scrap.reason.code",
        compute="_compute_allowed_reason_code_ids",
    )
    scrap_location_id = fields.Many2one(readonly=True)

    @api.depends("product_id", "product_id.categ_id")
    def _compute_allowed_reason_code_ids(self):
        for rec in self:
            codes = self.env["scrap.reason.code"]
            if rec.product_id:
                codes = codes.search(
                    [
                        "|",
                        ("product_category_ids", "=", False),
                        ("product_category_ids", "in", rec.product_id.categ_id.id),
                    ]
                )
            rec.allowed_reason_code_ids = codes

    @api.constrains("reason_code_id", "product_id")
    def _check_reason_code_id(self):
        for rec in self:
            if (
                rec.reason_code_id
                and rec.reason_code_id not in rec.allowed_reason_code_ids
            ):
                raise ValidationError(
                    _(
                        "The selected reason code is not allowed for this product category."
                    )
                )

    def _prepare_move_values(self):
        res = super(StockScrap, self)._prepare_move_values()
        res["reason_code_id"] = self.reason_code_id.id
        return res

    @api.onchange("reason_code_id")
    def _onchange_reason_code_id(self):
        if self.reason_code_id.location_id:
            self.scrap_location_id = self.reason_code_id.location_id

    def _update_scrap_reason_code_location(self, vals):
        if "reason_code_id" in vals:
            location_id = (
                self.env["scrap.reason.code"]
                .browse(vals.get("reason_code_id"))
                .location_id.id
            )
            if location_id:
                vals.update({"scrap_location_id": location_id})

    def write(self, vals):
        self._update_scrap_reason_code_location(vals)
        return super(StockScrap, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._update_scrap_reason_code_location(vals)
        return super().create(vals_list)
