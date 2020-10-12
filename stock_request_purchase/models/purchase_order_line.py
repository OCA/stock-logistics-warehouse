# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    stock_request_ids = fields.Many2many(
        comodel_name="stock.request", string="Stock Requests", copy=False
    )

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)

        for re in res:
            re["allocation_ids"] = [
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

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        vals = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        if "stock_request_id" in values:
            vals["stock_request_ids"] = [(4, values["stock_request_id"])]
        return vals

    @api.constrains("stock_request_ids")
    def _check_purchase_company_constrains(self):
        if any(
            any(req.company_id != pol.company_id for req in pol.stock_request_ids)
            for pol in self
        ):
            raise ValidationError(
                _(
                    "You cannot link a purchase order line "
                    "to a stock request that belongs to "
                    "another company."
                )
            )
