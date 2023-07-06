# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "analytic.mixin"]
    _order = "id desc"

    name = fields.Char(string="Description", tracking=True)
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        tracking=True,
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    product_qty = fields.Float(
        string="Quantity", tracking=True, digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Assigned to",
        store=True,
    )
    date_start = fields.Date(related="request_id.date_start", store=True)
    description = fields.Text(
        related="request_id.description",
        string="PR Description",
        store=True,
        readonly=False,
    )
    origin = fields.Char(
        related="request_id.origin", string="Source Document", store=True
    )
    date_required = fields.Date(
        string="Request Date",
        required=True,
        tracking=True,
        default=fields.Date.context_today,
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    specifications = fields.Text()
    request_state = fields.Selection(
        string="Request state",
        related="request_id.state",
        store=True,
    )
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Preferred supplier",
        compute="_compute_supplier_id",
        compute_sudo=True,
        store=True,
    )
    cancelled = fields.Boolean(readonly=True, default=False, copy=False)

    purchased_qty = fields.Float(
        string="RFQ/PO Qty",
        digits="Product Unit of Measure",
        compute="_compute_purchased_qty",
    )
    purchase_lines = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_request_line_id",
        column2="purchase_order_line_id",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )
    purchase_state = fields.Selection(
        compute="_compute_purchase_state",
        string="Purchase Status",
        selection=lambda self: self.env["purchase.order"]._fields["state"].selection,
        store=True,
    )
    move_dest_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="created_purchase_request_line_id",
        string="Downstream Moves",
    )

    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Orderpoint"
    )
    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_request_line_id",
        string="Purchase Request Allocation",
    )

    qty_in_progress = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity in progress.",
    )
    qty_done = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity completed",
    )
    qty_cancelled = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty_cancelled",
        store=True,
        help="Quantity cancelled",
    )
    qty_to_buy = fields.Boolean(
        compute="_compute_qty_to_buy",
        string="There is some pending qty to buy",
        store=True,
    )
    pending_qty_to_receive = fields.Float(
        compute="_compute_qty_to_buy",
        digits="Product Unit of Measure",
        copy=False,
        string="Pending Qty to Receive",
        store=True,
    )
    estimated_cost = fields.Monetary(
        currency_field="currency_id",
        default=0.0,
        help="Estimated cost of Purchase Request Line, not propagated to PO.",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        tracking=True,
    )

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "request_id.state",
        "product_qty",
    )
    def _compute_qty_to_buy(self):
        for pr in self:
            qty_to_buy = sum(pr.mapped("product_qty")) - sum(pr.mapped("qty_done"))
            pr.qty_to_buy = qty_to_buy > 0.0
            pr.pending_qty_to_receive = qty_to_buy

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty(self):
        for request in self:
            done_qty = sum(
                request.purchase_request_allocation_ids.mapped("allocated_product_qty")
            )
            open_qty = sum(
                request.purchase_request_allocation_ids.mapped("open_product_qty")
            )
            request.qty_done = done_qty
            request.qty_in_progress = open_qty

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.order_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty_cancelled(self):
        for request in self:
            if request.product_id.type != "service":
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.stock_move_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
            else:
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.purchase_line_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
                # done this way as i cannot track what was received before
                # cancelled the purchase order
                qty_cancelled -= request.qty_done
            if request.product_uom_id:
                request.qty_cancelled = (
                    max(
                        0,
                        request.product_id.uom_id._compute_quantity(
                            qty_cancelled, request.product_uom_id
                        ),
                    )
                    if request.purchase_request_allocation_ids
                    else 0
                )
            else:
                request.qty_cancelled = qty_cancelled

    @api.depends(
        "purchase_lines",
        "request_id.state",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False

    @api.depends("product_id", "product_id.seller_ids")
    def _compute_supplier_id(self):
        for rec in self:
            sellers = rec.product_id.seller_ids.filtered(
                lambda si, rec=rec: not si.company_id or si.company_id == rec.company_id
            )
            rec.supplier_id = sellers[0].partner_id if sellers else False

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(self.product_id.code, name)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name

    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def write(self, vals):
        res = super(PurchaseRequestLine, self).write(vals)
        if vals.get("cancelled"):
            requests = self.mapped("request_id")
            requests.check_auto_reject()
        return res

    def _compute_purchased_qty(self):
        for rec in self:
            rec.purchased_qty = 0.0
            for line in rec.purchase_lines.filtered(lambda x: x.state != "cancel"):
                if rec.product_uom_id and line.product_uom != rec.product_uom_id:
                    rec.purchased_qty += line.product_uom._compute_quantity(
                        line.product_qty, rec.product_uom_id
                    )
                else:
                    rec.purchased_qty += line.product_qty

    @api.depends("purchase_lines.state", "purchase_lines.order_id.state")
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any(po_line.state == "done" for po_line in rec.purchase_lines):
                    temp_purchase_state = "done"
                elif all(po_line.state == "cancel" for po_line in rec.purchase_lines):
                    temp_purchase_state = "cancel"
                elif any(po_line.state == "purchase" for po_line in rec.purchase_lines):
                    temp_purchase_state = "purchase"
                elif any(
                    po_line.state == "to approve" for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "to approve"
                elif any(po_line.state == "sent" for po_line in rec.purchase_lines):
                    temp_purchase_state = "sent"
                elif all(
                    po_line.state in ("draft", "cancel")
                    for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "draft"
            rec.purchase_state = temp_purchase_state

    @api.model
    def _get_supplier_min_qty(self, product, partner_id=False):
        seller_min_qty = 0.0
        if partner_id:
            seller = product.seller_ids.filtered(
                lambda r: r.partner_id == partner_id
            ).sorted(key=lambda r: r.min_qty)
        else:
            seller = product.seller_ids.sorted(key=lambda r: r.min_qty)
        if seller:
            seller_min_qty = seller[0].min_qty
        return seller_min_qty

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, new_pr_line=False):
        purchase_uom = po_line.product_uom or request_line.product_id.uom_po_id
        # TODO: Not implemented yet.
        #  Make sure we use the minimum quantity of the partner corresponding
        #  to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if not po_line.order_id.dest_address_id:
            supplierinfo_min_qty = self._get_supplier_min_qty(
                po_line.product_id, po_line.order_id.partner_id
            )

        rl_qty = 0.0
        # Recompute quantity by adding existing running procurements.
        if new_pr_line:
            rl_qty = po_line.product_uom_qty
        else:
            for prl in po_line.purchase_request_lines:
                for alloc in prl.purchase_request_allocation_ids:
                    rl_qty += alloc.product_uom_id._compute_quantity(
                        alloc.requested_product_uom_qty, purchase_uom
                    )
        qty = max(rl_qty, supplierinfo_min_qty)
        return qty

    def _can_be_deleted(self):
        self.ensure_one()
        return self.request_state == "draft"

    def unlink(self):
        if self.mapped("purchase_lines"):
            raise UserError(
                _("You cannot delete a record that refers to purchase lines!")
            )
        for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "You can only delete a purchase request line "
                        "if the purchase request is in draft state."
                    )
                )
        return super(PurchaseRequestLine, self).unlink()

    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref("purchase_request.view_purchase_request_line_details")
        return {
            "name": _("Detailed Line"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "purchase.request.line",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(
                self.env.context,
            ),
        }
