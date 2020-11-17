# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    @api.model
    def _get_default_picking_type(self):
        companies = self._context.get("allowed_company_ids", []).copy()
        companies.append(False)
        return (
            self.env["stock.picking.type"]
            .search(
                [
                    ("code", "=", "stock_request_order"),
                    "|",
                    ("warehouse_id.company_id", "in", companies),
                    ("warehouse_id", "=", False),
                ],
                limit=1,
            )
            .id
        )

    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Operation Type",
        default=_get_default_picking_type,
        required=True,
    )

    @api.onchange("warehouse_id")
    def onchange_warehouse_picking_id(self):
        if self.warehouse_id:
            picking_type_id = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "stock_request_order"),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ],
                limit=1,
            )
            if picking_type_id:
                self._origin.write({"picking_type_id": picking_type_id.id})

    @api.model
    def create(self, vals):
        if vals.get("warehouse_id", False):
            picking_type_id = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "stock_request_order"),
                    ("warehouse_id", "=", vals["warehouse_id"]),
                ],
                limit=1,
            )
            if picking_type_id:
                vals.update({"picking_type_id": picking_type_id.id})
        return super().create(vals)
