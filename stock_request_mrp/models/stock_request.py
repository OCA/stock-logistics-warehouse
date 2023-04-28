# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _inherit = "stock.request"

    production_ids = fields.Many2many(
        "mrp.production",
        "mrp_production_stock_request_rel",
        "stock_request_id",
        "mrp_production_id",
        string="Manufacturing Orders",
        readonly=True,
        copy=False,
    )
    production_count = fields.Integer(
        string="Manufacturing Orders count",
        compute="_compute_production_ids",
        readonly=True,
    )

    @api.depends("production_ids")
    def _compute_production_ids(self):
        for request in self:
            request.production_count = len(request.production_ids)

    @api.constrains("production_ids", "company_id")
    def _check_production_company_constrains(self):
        if any(
            any(
                production.company_id != req.company_id
                for production in req.production_ids
            )
            for req in self
        ):
            raise ValidationError(
                _(
                    "You have linked to a Manufacture Order "
                    "that belongs to another company."
                )
            )

    def action_view_mrp_production(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.mrp_production_action"
        )
        productions = self.mapped("production_ids")
        if len(productions) > 1:
            action["domain"] = [("id", "in", productions.ids)]
        elif productions:
            action["views"] = [
                (self.env.ref("mrp.mrp_production_form_view").id, "form")
            ]
            action["res_id"] = productions.id
        return action
