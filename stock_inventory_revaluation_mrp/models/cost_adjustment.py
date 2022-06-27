# Copyright 2021-2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class CostAdjustment(models.Model):
    _inherit = "stock.cost.adjustment"

    bom_impact_ids = fields.One2many(
        "stock.cost.adjustment.detail",
        "cost_adjustment_id",
    )

    def action_cancel_draft(self):
        self.bom_impact_ids.unlink()
        super().action_cancel_draft()

    def action_open_cost_adjustment_details(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Cost Adjustment Detail"),
            "res_model": "stock.cost.adjustment.detail",
            "context": {
                "default_is_editable": False,
                "default_cost_adjustment_id": self.id,
                "default_company_id": self.company_id.id,
                "search_default_group_by_product_id": 1,
            },
            "domain": [("cost_adjustment_id", "=", self.id)],
            "view_id": self.env.ref(
                "stock_inventory_revaluation_mrp.cost_adjustment_detail_mrp_view_tree"
            ).id,
        }

    def action_compute_impact(self):
        self.compute_impact()

    def compute_impact(self):
        self.bom_impact_ids.unlink()
        for line in self.line_ids.filtered(lambda x: not x.is_automatically_added):
            line._populate_bom_impact_details(line.product_id)
        self.line_ids._populate_impacted_products()
        self.line_ids.action_refresh_quantity()

    def action_post(self):
        res = super().action_post()
        for line in self.line_ids:
            for bom in line.product_id.bom_line_ids.mapped("bom_id"):
                if bom.product_id:
                    bom.product_id.sudo().button_bom_cost()
                else:
                    bom.product_tmpl_id.sudo().button_bom_cost()
                for parent_bom in (
                    bom.product_id.bom_line_ids.mapped("bom_id")
                    if bom.product_id
                    else bom.product_tmpl_id.bom_line_ids.mapped("bom_id")
                ):
                    if parent_bom.product_id:
                        parent_bom.product_id.sudo().button_bom_cost()
                    else:
                        parent_bom.product_tmpl_id.sudo().button_bom_cost()
        return res
