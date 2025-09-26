# Copyright 2017-25 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# Copyright 2025 OERP Canada <https://www.oerp.ca>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SlotVerificationRequest(models.Model):
    _name = "stock.slot.verification.request"
    _inherit = "mail.thread"
    _description = "Slot Verification Request"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals.get("name") == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code(
                        "stock.slot.verification.request"
                    )
                    or "/"
                )
        return super().create(vals_list)

    def _compute_involved_move_line_count(self):
        for rec in self:
            rec.involved_move_line_count = len(rec.involved_move_line_ids)

    def _compute_involved_quant_count(self):
        for rec in self:
            rec.involved_quant_count = len(rec.involved_quant_ids)

    def _compute_created_inventory_count(self):
        for rec in self:
            rec.created_inventory_count = len(rec.created_inventory_ids)

    name = fields.Char(
        default="/",
        required=True,
        readonly=True,
    )
    inventory_id = fields.Many2one(
        comodel_name="stock.inventory", string="Inventory Adjustment", readonly=True
    )
    quant_id = fields.Many2one(
        comodel_name="stock.quant", string="Stock Line", readonly=True
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location",
        required=True,
        readonly=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("wait", "Waiting Actions"),
            ("open", "In Progress"),
            ("cancelled", "Cancelled"),
            ("done", "Solved"),
        ],
        string="Status",
        default="wait",
        tracking=True,
    )
    responsible_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        tracking=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        readonly=True,
        tracking=True,
    )
    product_name = fields.Char(
        "Product Name", related="product_id.name", store=True, translate=False
    )
    product_default_code = fields.Char(
        related="product_id.default_code", store=True, translate=False
    )
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot",
        readonly=True,
        tracking=True,
    )
    notes = fields.Text()
    involved_move_line_ids = fields.Many2many(
        comodel_name="stock.move.line",
        relation="slot_verification_move_involved_rel",
        column1="slot_verification_request_id",
        column2="move_line_id",
        string="Involved Stock Moves",
        compute="_compute_involved_move_lines",
        store=False,
    )
    involved_move_line_count = fields.Integer(
        compute="_compute_involved_move_line_count"
    )
    involved_quant_ids = fields.Many2many(
        comodel_name="stock.quant",
        relation="slot_verification_inv_line_involved_rel",
        column1="slot_verification_request_id",
        column2="quant_id",
        string="Involved Inventory Quants",
        compute="_compute_involved_quants",
        store=False,
    )
    involved_quant_count = fields.Integer(compute="_compute_involved_quant_count")
    created_inventory_ids = fields.One2many(
        comodel_name="stock.inventory",
        string="Created Inventories",
        inverse_name="solving_slot_verification_request_id",
        help="These inventory adjustments were created from this SVR.",
    )
    created_inventory_count = fields.Integer(compute="_compute_created_inventory_count")
    processed_by = fields.Many2one(
        "res.users",
        readonly=True,
        copy=False,
        help="User who has solved or cancelled the request.",
    )

    @api.depends("location_id", "product_id", "lot_id", "state")
    def _compute_involved_move_lines(self):
        for rec in self:
            if rec.state == "open":
                rec.involved_move_line_ids = self.env["stock.move.line"].search(
                    rec._get_involved_move_lines_domain()
                )
            else:
                rec.involved_move_line_ids = self.env["stock.move.line"]

    @api.depends("location_id", "product_id", "lot_id", "state")
    def _compute_involved_quants(self):
        for rec in self:
            if rec.state == "open":
                rec.involved_quant_ids = self.env["stock.quant"].search(
                    rec._get_involved_quants_domain()
                )
            else:
                rec.involved_quant_ids = self.env["stock.quant"]

    def _get_involved_move_lines_domain(self):
        domain = [
            "|",
            ("location_id", "=", self.location_id.id),
            ("location_dest_id", "=", self.location_id.id),
        ]
        if self.product_id:
            domain.append(("product_id", "=", self.product_id.id))
        if self.lot_id:
            domain.append(("lot_id", "=", self.lot_id.id))
        return domain

    def _get_involved_quants_domain(self):
        domain = [("location_id", "=", self.location_id.id)]
        if self.product_id:
            domain.append(("product_id", "=", self.product_id.id))
        if self.lot_id:
            domain.append(("lot_id", "=", self.lot_id.id))
        return domain

    def action_confirm(self):
        self.write({"state": "open"})
        return True

    def action_cancel(self):
        self.write(
            {
                "state": "cancelled",
                "processed_by": self.env.uid,
            }
        )
        if self.quant_id:
            self.quant_id.requested_verification = False
        return True

    def action_solved(self):
        self.write(
            {
                "state": "done",
                "processed_by": self.env.uid,
            }
        )
        if self.quant_id:
            self.quant_id.requested_verification = False
        return True

    def action_view_move_lines(self):
        action = self.env.ref(
            "stock_inventory_verification_request.action_move_lines_svr"
        ).read()[0]
        moves_ids = self.mapped("involved_move_line_ids").ids
        result = action
        result["domain"] = [("id", "in", moves_ids)]
        return result

    def action_view_quants(self):
        action = self.env.ref(
            "stock_inventory_verification_request.action_quant_line_tree"
        )
        result = action.read()[0]
        result["context"] = {}
        quant_ids = self.mapped("involved_quant_ids").ids
        result["domain"] = [("id", "in", quant_ids)]
        return result

    def action_create_inventory_adjustment(self):
        self.ensure_one()
        inventory = (
            self.env["stock.inventory"]
            .sudo()
            .create(
                {
                    "name": f"Inventory Adjustment from {self.name}",
                    "product_selection": "one" if self.product_id else "all",
                    "location_ids": [(6, 0, [self.location_id.id])]
                    if self.location_id
                    else False,
                    "product_ids": [(6, 0, [self.product_id.id])]
                    if self.product_id
                    else False,
                    "solving_slot_verification_request_id": self.id,
                    "company_id": self.company_id.id,
                }
            )
        )
        action = self.env.ref("stock_inventory.action_view_inventory_group_form")
        result = action.read()[0]
        res = self.env.ref("stock_inventory.view_inventory_group_form", False)
        result["views"] = [(res and res.id or False, "form")]
        result["res_id"] = inventory.id
        return result

    def action_view_inventories(self):
        action = self.env.ref("stock_inventory.action_view_inventory_group_form", False)
        result = action.read()[0]
        result["context"] = {}
        inventory_ids = self.mapped("created_inventory_ids").ids
        if len(inventory_ids) > 1:
            result["domain"] = [("id", "in", inventory_ids)]
        elif len(inventory_ids) == 1:
            res = self.env.ref("stock_inventory.view_inventory_group_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = inventory_ids and inventory_ids[0] or False
        return result
