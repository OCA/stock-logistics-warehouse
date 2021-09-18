# Copyright 2018-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    orderpoint_ids = fields.Many2many(
        comodel_name="stock.warehouse.orderpoint",
        string="Orderpoints",
        copy=False,
        readonly=True,
    )

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        vals = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        # If the procurement was run directly by a reordering rule.
        if "orderpoint_id" in values and values["orderpoint_id"].id:
            vals["orderpoint_ids"] = [(4, values["orderpoint_id"].id)]
        # If the procurement was run by a stock move.
        elif "orderpoint_ids" in values:
            vals["orderpoint_ids"] = [(4, o.id) for o in values["orderpoint_ids"]]
        return vals
