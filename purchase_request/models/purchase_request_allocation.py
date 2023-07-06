# Copyright 2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models


class PurchaseRequestAllocation(models.Model):
    _name = "purchase.request.allocation"
    _description = "Purchase Request Allocation"

    purchase_request_line_id = fields.Many2one(
        string="Purchase Request Line",
        comodel_name="purchase.request.line",
        required=True,
        ondelete="cascade",
        copy=True,
        index=True,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        readonly=True,
        related="purchase_request_line_id.request_id.company_id",
        store=True,
        index=True,
    )
    stock_move_id = fields.Many2one(
        string="Stock Move",
        comodel_name="stock.move",
        ondelete="cascade",
        index=True,
    )
    purchase_line_id = fields.Many2one(
        string="Purchase Line",
        comodel_name="purchase.order.line",
        copy=True,
        ondelete="cascade",
        help="Service Purchase Order Line",
        index=True,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        related="purchase_request_line_id.product_id",
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        string="UoM",
        comodel_name="uom.uom",
        related="purchase_request_line_id.product_uom_id",
        readonly=True,
        required=True,
    )
    requested_product_uom_qty = fields.Float(
        string="Requested Quantity",
        help="Quantity of the purchase request line allocated to the"
        "stock move, in the UoM of the Purchase Request Line",
    )

    allocated_product_qty = fields.Float(
        string="Allocated Quantity",
        copy=False,
        help="Quantity of the purchase request line allocated to the stock"
        "move, in the default UoM of the product",
    )
    open_product_qty = fields.Float(
        string="Open Quantity", compute="_compute_open_product_qty"
    )

    purchase_state = fields.Selection(related="purchase_line_id.state")

    @api.depends(
        "requested_product_uom_qty",
        "allocated_product_qty",
        "stock_move_id",
        "stock_move_id.state",
        "stock_move_id.product_uom_qty",
        "stock_move_id.move_line_ids.qty_done",
        "purchase_line_id",
        "purchase_line_id.qty_received",
        "purchase_state",
    )
    def _compute_open_product_qty(self):
        for rec in self:
            if rec.purchase_state in ["cancel", "done"]:
                rec.open_product_qty = 0.0
            else:
                rec.open_product_qty = (
                    rec.requested_product_uom_qty - rec.allocated_product_qty
                )
                if rec.open_product_qty < 0.0:
                    rec.open_product_qty = 0.0

    @api.model
    def _purchase_request_confirm_done_message_content(self, message_data):
        message = ""
        message += _(
            "From last reception this quantity has been "
            "allocated to this purchase request"
        )
        message += "<ul>"
        message += _(
            "<li><b>%(product_name)s</b>: "
            "Received quantity %(product_qty)s %(product_uom)s</li>"
        ) % {
            "product_name": message_data["product_name"],
            "product_qty": message_data["product_qty"],
            "product_uom": message_data["product_uom"],
        }
        message += "</ul>"
        return message

    def _prepare_message_data(self, po_line, request, allocated_qty):
        return {
            "request_name": request.name,
            "po_name": po_line.order_id.name,
            "product_name": po_line.product_id.name_get()[0][1],
            "product_qty": allocated_qty,
            "product_uom": po_line.product_uom.name,
        }

    def _notify_allocation(self, allocated_qty):
        if not allocated_qty:
            return
        for allocation in self:
            request = allocation.purchase_request_line_id.request_id
            po_line = allocation.purchase_line_id
            message_data = self._prepare_message_data(po_line, request, allocated_qty)
            message = self._purchase_request_confirm_done_message_content(message_data)
            request.message_post(
                body=message, subtype_id=self.env.ref("mail.mt_comment").id
            )
