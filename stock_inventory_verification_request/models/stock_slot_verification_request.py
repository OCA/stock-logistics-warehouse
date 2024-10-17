# Copyright 2017-20 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SlotVerificationRequest(models.Model):
    _name = "stock.slot.verification.request"
    _inherit = "mail.thread"
    _description = "Slot Verification Request"

    @api.model
    def _default_company(self):
        company_id = self.env["res.company"]._company_default_get(self._name)
        return company_id

    @api.model
    def create(self, vals):
        if not vals.get("name") or vals.get("name") == "/":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("stock.slot.verification.request")
                or "/"
            )
        return super(SlotVerificationRequest, self).create(vals)

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
        states={"wait": [("readonly", False)]},
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
        states={"wait": [("readonly", False)]},
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_default_company,
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
        states={"wait": [("readonly", False)]},
        tracking=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot",
        readonly=True,
        states={"wait": [("readonly", False)]},
        tracking=True,
    )
    notes = fields.Text()
    involved_move_line_ids = fields.Many2many(
        comodel_name="stock.move.line",
        relation="slot_verification_move_involved_rel",
        column1="slot_verification_request_id",
        column2="move_line_id",
        string="Involved Stock Moves",
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
    )
    involved_quant_count = fields.Integer(compute="_compute_involved_quant_count")
    created_inventory_ids = fields.One2many(
        comodel_name="stock.inventory",
        string="Created Inventories",
        inverse_name="solving_slot_verification_request_id",
        help="These inventory adjustment were created from this SVR.",
    )
    created_inventory_count = fields.Integer(compute="_compute_created_inventory_count")

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

    def _get_involved_quants_and_locations(self):
        involved_move_lines = self.env["stock.move.line"].search(
            self._get_involved_move_lines_domain()
        )
        involved_quants = self.env["stock.quant"].search(
            self._get_involved_quants_domain()
        )
        return involved_move_lines, involved_quants

    def action_confirm(self):
        self.write({"state": "open"})
        for rec in self:
            (
                involved_moves_lines,
                involved_quants,
            ) = rec._get_involved_quants_and_locations()
            rec.involved_move_line_ids = involved_moves_lines
            rec.involved_quant_ids = involved_quants
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        if self.quant_id:
            self.quant_id.requested_verification = False
        return True

    def action_solved(self):
        self.write({"state": "done"})
        if self.quant_id:
            self.quant_id.requested_verification = False
        return True

    def action_view_move_lines(self):
        action = self.env.ref("stock.stock_move_line_action")
        result = action.read()[0]
        result["context"] = {}
        moves_ids = self.mapped("involved_move_line_ids").ids
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
                    "name": "Inventory Adjustment from %s" % self.name,
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
