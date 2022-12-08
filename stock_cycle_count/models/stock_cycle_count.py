# Copyright 2017-18 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockCycleCount(models.Model):
    _name = "stock.cycle.count"
    _description = "Stock Cycle Counts"
    _inherit = "mail.thread"
    _order = "id desc"

    name = fields.Char(string="Name", readonly=True)
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    responsible_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        readonly=True,
        states={"draft": [("readonly", False)]},
        track_visibility="onchange",
    )
    date_deadline = fields.Date(
        string="Required Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        track_visibility="onchange",
    )
    cycle_count_rule_id = fields.Many2one(
        comodel_name="stock.cycle.count.rule",
        string="Cycle count rule",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        track_visibility="onchange",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Planned"),
            ("open", "Execution"),
            ("cancelled", "Cancelled"),
            ("done", "Done"),
        ],
        string="State",
        default="draft",
        track_visibility="onchange",
    )
    stock_adjustment_ids = fields.One2many(
        comodel_name="stock.inventory",
        inverse_name="cycle_count_id",
        string="Inventory Adjustment",
        track_visibility="onchange",
    )
    inventory_adj_count = fields.Integer(compute="_compute_inventory_adj_count")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )

    @api.depends("stock_adjustment_ids")
    def _compute_inventory_adj_count(self):
        for rec in self:
            rec.inventory_adj_count = len(rec.stock_adjustment_ids)

    def do_cancel(self):
        self.write({"state": "cancelled"})

    def _prepare_inventory_adjustment(self):
        self.ensure_one()
        return {
            "name": "INV/{}".format(self.name),
            "cycle_count_id": self.id,
            "location_ids": [(4, self.location_id.id)],
            "exclude_sublocation": True,
        }

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code("stock.cycle.count") or ""
        return super(StockCycleCount, self).create(vals)

    def action_create_inventory_adjustment(self):
        if any([s != "draft" for s in self.mapped("state")]):
            raise UserError(_("You can only confirm cycle counts in state 'Planned'."))
        for rec in self:
            data = rec._prepare_inventory_adjustment()
            self.env["stock.inventory"].create(data)
        self.write({"state": "open"})
        return True

    def action_view_inventory(self):
        action = self.env.ref("stock.action_inventory_form")
        result = action.read()[0]
        result["context"] = {}
        adjustment_ids = self.mapped("stock_adjustment_ids").ids
        if len(adjustment_ids) > 1:
            result["domain"] = [("id", "in", adjustment_ids)]
        elif len(adjustment_ids) == 1:
            res = self.env.ref("stock.view_inventory_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = adjustment_ids and adjustment_ids[0] or False
        return result
