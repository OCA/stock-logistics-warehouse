# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    stock_request_ids = fields.Many2many(
        "stock.request",
        "mrp_production_stock_request_rel",
        "mrp_production_id",
        "stock_request_id",
        string="Stock Requests",
    )
    stock_request_count = fields.Integer(
        "Stock Request #", compute="_compute_stock_request_ids"
    )

    @api.depends("stock_request_ids")
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_count = len(rec.stock_request_ids)

    def _get_stock_requests(self):
        """Get all stock requests from action (allows inheritance by other modules)."""
        return self.mapped("stock_request_ids")

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_request.action_stock_request_form"
        )
        requests = self.mapped("stock_request_ids")
        requests = self._get_stock_requests()
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action

    def _get_move_finished_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        byproduct_id=False,
        cost_share=0,
    ):
        res = super()._get_move_finished_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id=operation_id,
            byproduct_id=byproduct_id,
            cost_share=cost_share,
        )
        if self.stock_request_ids:
            res["allocation_ids"] = [
                (
                    0,
                    0,
                    {
                        "stock_request_id": request.id,
                        "requested_product_uom_qty": request.product_qty,
                    },
                )
                for request in self.stock_request_ids
            ]
        return res
