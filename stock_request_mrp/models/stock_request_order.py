# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    production_ids = fields.One2many(
        "mrp.production",
        compute="_compute_production_ids",
        string="Manufacturing Orders",
        readonly=True,
    )
    production_count = fields.Integer(
        string="Manufacturing Orders count",
        compute="_compute_production_ids",
        readonly=True,
    )

    @api.depends("stock_request_ids")
    def _compute_production_ids(self):
        for req in self:
            req.production_ids = req.stock_request_ids.mapped("production_ids")
            req.production_count = len(req.production_ids)

    def action_view_mrp_production(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.mrp_production_action"
        )
        productions = self.mapped("production_ids")
        if len(productions) > 1:
            action["domain"] = [("id", "in", productions.ids)]
            action["views"] = [
                (self.env.ref("mrp.mrp_production_tree_view").id, "tree"),
                (self.env.ref("mrp.mrp_production_form_view").id, "form"),
            ]
        elif productions:
            action["views"] = [
                (self.env.ref("mrp.mrp_production_form_view").id, "form")
            ]
            action["res_id"] = productions.id
        return action
