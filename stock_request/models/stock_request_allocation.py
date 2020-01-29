# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestAllocation(models.Model):
    _name = "stock.request.allocation"
    _description = "Stock Request Allocation"

    stock_request_id = fields.Many2one(
        string="Stock Request",
        comodel_name="stock.request",
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        readonly=True,
        related="stock_request_id.company_id",
        store=True,
    )
    stock_move_id = fields.Many2one(
        string="Stock Move",
        comodel_name="stock.move",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        related="stock_request_id.product_id",
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        string="UoM",
        comodel_name="uom.uom",
        related="stock_request_id.product_uom_id",
        readonly=True,
    )
    requested_product_uom_qty = fields.Float(
        "Requested Quantity (UoM)",
        help="Quantity of the stock request allocated to the stock move, "
        "in the UoM of the Stock Request",
    )
    requested_product_qty = fields.Float(
        "Requested Quantity",
        help="Quantity of the stock request allocated to the stock move, "
        "in the default UoM of the product",
        compute="_compute_requested_product_qty",
    )
    allocated_product_qty = fields.Float(
        "Allocated Quantity",
        help="Quantity of the stock request allocated to the stock move, "
        "in the default UoM of the product",
    )
    open_product_qty = fields.Float(
        "Open Quantity", compute="_compute_open_product_qty"
    )

    @api.depends(
        "stock_request_id.product_id",
        "stock_request_id.product_uom_id",
        "requested_product_uom_qty",
    )
    def _compute_requested_product_qty(self):
        for rec in self:
            rec.requested_product_qty = rec.product_uom_id._compute_quantity(
                rec.requested_product_uom_qty, rec.product_id.uom_id
            )

    @api.depends(
        "requested_product_qty",
        "allocated_product_qty",
        "stock_move_id",
        "stock_move_id.state",
    )
    def _compute_open_product_qty(self):
        for rec in self:
            if rec.stock_move_id.state == "cancel":
                rec.open_product_qty = 0.0
            else:
                rec.open_product_qty = (
                    rec.requested_product_qty - rec.allocated_product_qty
                )
                if rec.open_product_qty < 0.0:
                    rec.open_product_qty = 0.0
