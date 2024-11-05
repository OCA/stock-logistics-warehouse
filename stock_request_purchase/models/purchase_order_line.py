# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_round


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    stock_request_ids = fields.Many2many(
        comodel_name="stock.request", string="Stock Requests", copy=False
    )

    def unlink(self):
        """
        Cancel the stock.request
        related to the purchase order line
        because it does not occur automatically
        and causes inconsistency by keeping the SR state as 'In Progress' (open).
        """
        stock_request_to_cancel = self.env["stock.request"]
        for purchase_line in self:
            stock_request_to_cancel |= purchase_line.stock_request_ids
        res = super().unlink()
        if stock_request_to_cancel:
            stock_request_to_cancel.action_cancel()
        return res

    def _prepare_stock_moves(self, picking):
        """We define the allocation_ids with the corresponding quantity."""
        res = super()._prepare_stock_moves(picking)
        if not self.stock_request_ids:
            return res
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        requests_qty = sum(self.stock_request_ids.mapped("product_qty"))
        moves_qty = sum(re["product_uom_qty"] for re in res)
        diff_qty = moves_qty - requests_qty
        for re in res:
            allocations_data = []
            for request in self.stock_request_ids:
                qty = request.product_qty
                # Only add the extra (proportional) quantity if there is pending qty
                if not float_is_zero(diff_qty, precision_digits=precision):
                    extra_qty = diff_qty * (request.product_qty / requests_qty)
                    extra_qty = float_round(extra_qty, precision_digits=precision)
                    qty += extra_qty
                allocations_data.append(
                    (
                        0,
                        0,
                        {
                            "stock_request_id": request.id,
                            "requested_product_uom_qty": qty,
                        },
                    )
                )
            re["allocation_ids"] = allocations_data
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
