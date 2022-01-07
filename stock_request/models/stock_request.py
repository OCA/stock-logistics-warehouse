# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

REQUEST_STATES = [
    ("draft", "Draft"),
    ("open", "In progress"),
    ("done", "Done"),
    ("cancel", "Cancelled"),
]


class StockRequest(models.Model):
    _name = "stock.request"
    _description = "Stock Request"
    _inherit = "stock.request.abstract"
    _order = "id desc"

    def __get_request_states(self):
        return REQUEST_STATES

    def _get_request_states(self):
        return self.__get_request_states()

    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @staticmethod
    def _get_expected_date():
        return fields.Datetime.now()

    name = fields.Char(states={"draft": [("readonly", False)]})
    state = fields.Selection(
        selection=_get_request_states,
        string="Status",
        copy=False,
        default="draft",
        index=True,
        readonly=True,
        tracking=True,
    )
    requested_by = fields.Many2one(
        "res.users",
        "Requested by",
        required=True,
        tracking=True,
        default=lambda s: s._get_default_requested_by(),
    )
    expected_date = fields.Datetime(
        "Expected Date",
        index=True,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Date when you expect to receive the goods.",
    )
    picking_policy = fields.Selection(
        [
            ("direct", "Receive each product when available"),
            ("one", "Receive all products at once"),
        ],
        string="Shipping Policy",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="direct",
    )
    move_ids = fields.One2many(
        comodel_name="stock.move",
        compute="_compute_move_ids",
        string="Stock Moves",
        readonly=True,
    )
    picking_ids = fields.One2many(
        "stock.picking",
        compute="_compute_picking_ids",
        string="Pickings",
        readonly=True,
    )
    qty_in_progress = fields.Float(
        "Qty In Progress",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity in progress.",
    )
    qty_done = fields.Float(
        "Qty Done",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity completed",
    )
    qty_cancelled = fields.Float(
        "Qty Cancelled",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity cancelled",
    )
    picking_count = fields.Integer(
        string="Delivery Orders",
        compute="_compute_picking_ids",
        readonly=True,
    )
    allocation_ids = fields.One2many(
        comodel_name="stock.request.allocation",
        inverse_name="stock_request_id",
        string="Stock Request Allocation",
    )
    order_id = fields.Many2one("stock.request.order", readonly=True)
    warehouse_id = fields.Many2one(
        states={"draft": [("readonly", False)]}, readonly=True
    )
    location_id = fields.Many2one(
        states={"draft": [("readonly", False)]}, readonly=True
    )
    product_id = fields.Many2one(states={"draft": [("readonly", False)]}, readonly=True)
    product_uom_id = fields.Many2one(
        states={"draft": [("readonly", False)]}, readonly=True
    )
    product_uom_qty = fields.Float(
        states={"draft": [("readonly", False)]}, readonly=True
    )
    procurement_group_id = fields.Many2one(
        states={"draft": [("readonly", False)]}, readonly=True
    )
    company_id = fields.Many2one(states={"draft": [("readonly", False)]}, readonly=True)
    route_id = fields.Many2one(states={"draft": [("readonly", False)]}, readonly=True)

    _sql_constraints = [
        ("name_uniq", "unique(name, company_id)", "Stock Request name must be unique")
    ]

    @api.depends("allocation_ids", "allocation_ids.stock_move_id")
    def _compute_move_ids(self):
        for request in self:
            request.move_ids = request.allocation_ids.mapped("stock_move_id")

    @api.depends(
        "allocation_ids",
        "allocation_ids.stock_move_id",
        "allocation_ids.stock_move_id.picking_id",
    )
    def _compute_picking_ids(self):
        for request in self:
            request.picking_count = 0
            request.picking_ids = self.env["stock.picking"]
            request.picking_ids = request.move_ids.filtered(
                lambda m: m.state != "cancel"
            ).mapped("picking_id")
            request.picking_count = len(request.picking_ids)

    @api.depends(
        "allocation_ids",
        "allocation_ids.stock_move_id.state",
        "allocation_ids.stock_move_id.move_line_ids",
        "allocation_ids.stock_move_id.move_line_ids.qty_done",
    )
    def _compute_qty(self):
        for request in self:
            incoming_qty = 0.0
            other_qty = 0.0
            for allocation in request.allocation_ids:
                if allocation.stock_move_id.picking_code == "incoming":
                    incoming_qty += allocation.allocated_product_qty
                else:
                    other_qty += allocation.allocated_product_qty
            done_qty = abs(other_qty - incoming_qty)
            open_qty = sum(request.allocation_ids.mapped("open_product_qty"))
            uom = request.product_id.uom_id
            request.qty_done = uom._compute_quantity(done_qty, request.product_uom_id)
            request.qty_in_progress = uom._compute_quantity(
                open_qty, request.product_uom_id
            )
            request.qty_cancelled = (
                max(
                    0,
                    uom._compute_quantity(
                        request.product_qty - done_qty - open_qty,
                        request.product_uom_id,
                    ),
                )
                if request.allocation_ids
                else 0
            )

    @api.constrains("order_id", "requested_by")
    def check_order_requested_by(self):
        if self.order_id and self.order_id.requested_by != self.requested_by:
            raise ValidationError(_("Requested by must be equal to the order"))

    @api.constrains("order_id", "warehouse_id")
    def check_order_warehouse_id(self):
        if self.order_id and self.order_id.warehouse_id != self.warehouse_id:
            raise ValidationError(_("Warehouse must be equal to the order"))

    @api.constrains("order_id", "location_id")
    def check_order_location(self):
        if self.order_id and self.order_id.location_id != self.location_id:
            raise ValidationError(_("Location must be equal to the order"))

    @api.constrains("order_id", "procurement_group_id")
    def check_order_procurement_group(self):
        if (
            self.order_id
            and self.order_id.procurement_group_id != self.procurement_group_id
        ):
            raise ValidationError(_("Procurement group must be equal to the order"))

    @api.constrains("order_id", "company_id")
    def check_order_company(self):
        if self.order_id and self.order_id.company_id != self.company_id:
            raise ValidationError(_("Company must be equal to the order"))

    @api.constrains("order_id", "expected_date")
    def check_order_expected_date(self):
        if self.order_id and self.order_id.expected_date != self.expected_date:
            raise ValidationError(_("Expected date must be equal to the order"))

    @api.constrains("order_id", "picking_policy")
    def check_order_picking_policy(self):
        if self.order_id and self.order_id.picking_policy != self.picking_policy:
            raise ValidationError(_("The picking policy must be equal to the order"))

    def _action_confirm(self):
        self._action_launch_procurement_rule()
        self.write({"state": "open"})

    def action_confirm(self):
        self._action_confirm()
        return True

    def action_draft(self):
        self.write({"state": "draft"})
        return True

    def action_cancel(self):
        self.sudo().mapped("move_ids")._action_cancel()
        self.write({"state": "cancel"})
        return True

    def action_done(self):
        self.write({"state": "done"})
        self.mapped("order_id").check_done()
        return True

    def check_done(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for request in self:
            allocated_qty = sum(request.allocation_ids.mapped("allocated_product_qty"))
            qty_done = request.product_id.uom_id._compute_quantity(
                allocated_qty, request.product_uom_id
            )
            if (
                float_compare(
                    qty_done, request.product_uom_qty, precision_digits=precision
                )
                >= 0
            ):
                request.action_done()
            elif request._check_done_allocation():
                request.action_done()
        return True

    def _check_done_allocation(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        self.ensure_one()
        return (
            self.allocation_ids
            and float_compare(self.qty_cancelled, 0, precision_digits=precision) > 0
        )

    def _prepare_procurement_values(self, group_id=False):

        """Prepare specific key for moves or other components that
        will be created from a procurement rule
        coming from a stock request. This method could be override
        in order to add other custom key that could be used in
        move/po creation.
        """
        return {
            "date_planned": self.expected_date,
            "warehouse_id": self.warehouse_id,
            "stock_request_allocation_ids": self.id,
            "group_id": group_id or self.procurement_group_id.id or False,
            "route_ids": self.route_id,
            "stock_request_id": self.id,
        }

    def _skip_procurement(self):
        return self.state != "draft" or self.product_id.type not in ("consu", "product")

    def _action_launch_procurement_rule(self):
        """
        Launch procurement group run method with required/custom
        fields genrated by a
        stock request. procurement group will launch '_run_move',
        '_run_buy' or '_run_manufacture'
        depending on the stock request product rule.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        errors = []
        for request in self:
            if request._skip_procurement():
                continue
            qty = 0.0
            for move in request.move_ids.filtered(lambda r: r.state != "cancel"):
                qty += move.product_qty

            if float_compare(qty, request.product_qty, precision_digits=precision) >= 0:
                continue

            values = request._prepare_procurement_values(
                group_id=request.procurement_group_id
            )
            try:
                procurements = []
                procurements.append(
                    self.env["procurement.group"].Procurement(
                        request.product_id,
                        request.product_uom_qty,
                        request.product_uom_id,
                        request.location_id,
                        request.name,
                        request.name,
                        self.env.company,
                        values,
                    )
                )
                self.env["procurement.group"].sudo().run(procurements)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError("\n".join(errors))
        return True

    def action_view_transfer(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        pickings = self.mapped("picking_ids")
        if len(pickings) > 1:
            action["domain"] = [("id", "in", pickings.ids)]
        elif pickings:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = pickings.id
        return action

    @api.model
    def create(self, vals):
        upd_vals = vals.copy()
        if upd_vals.get("name", "/") == "/":
            upd_vals["name"] = self.env["ir.sequence"].next_by_code("stock.request")
        if "order_id" in upd_vals:
            order_id = self.env["stock.request.order"].browse(upd_vals["order_id"])
            upd_vals["expected_date"] = order_id.expected_date
        else:
            upd_vals["expected_date"] = self._get_expected_date()
        return super().create(upd_vals)

    def unlink(self):
        if self.filtered(lambda r: r.state != "draft"):
            raise UserError(_("Only requests on draft state can be unlinked"))
        return super(StockRequest, self).unlink()
