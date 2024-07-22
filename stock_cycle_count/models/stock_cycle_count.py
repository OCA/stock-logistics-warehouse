# Copyright 2017-18 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockCycleCount(models.Model):
    _name = "stock.cycle.count"
    _description = "Stock Cycle Counts"
    _inherit = "mail.thread"
    _order = "id desc"

    name = fields.Char(readonly=True)
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
        tracking=True,
    )
    date_deadline = fields.Date(
        string="Required Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True,
    )
    automatic_deadline_date = fields.Date(
        string="Automatic Required Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    manual_deadline_date = fields.Date(
        string="Manual Required Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    cycle_count_rule_id = fields.Many2one(
        comodel_name="stock.cycle.count.rule",
        string="Cycle count rule",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Planned"),
            ("open", "Execution"),
            ("cancelled", "Cancelled"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
    )
    stock_adjustment_ids = fields.One2many(
        comodel_name="stock.inventory",
        inverse_name="cycle_count_id",
        string="Inventory Adjustment",
        tracking=True,
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
            "responsible_id": self.responsible_id.id,
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("stock.cycle.count") or ""
            )
        return super().create(vals_list)

    def action_create_inventory_adjustment(self):
        if any([state != "draft" for state in self.mapped("state")]):
            raise UserError(_("You can only confirm cycle counts in state 'Planned'."))
        for rec in self:
            data = rec._prepare_inventory_adjustment()
            inv = self.env["stock.inventory"].create(data)
            if rec.company_id.auto_start_inventory_from_cycle_count:
                try:
                    inv.action_state_to_in_progress()
                except Exception as e:
                    _logger.info("Error when beginning an adjustment: %s", str(e))
        self.write({"state": "open"})
        return True

    def action_view_inventory(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_inventory.action_view_inventory_group_form"
        )
        action["context"] = {}
        adjustment_ids = self.mapped("stock_adjustment_ids").ids
        if len(adjustment_ids) > 1:
            action["domain"] = [("id", "in", adjustment_ids)]
        elif len(adjustment_ids) == 1:
            res = self.env.ref("stock_inventory.view_inventory_group_form", False)
            action["views"] = [(res and res.id or False, "form")]
            action["res_id"] = adjustment_ids and adjustment_ids[0] or False
        return action

    @api.depends("automatic_deadline_date", "manual_deadline_date")
    def _compute_date_deadline(self):
        for rec in self:
            if rec.manual_deadline_date:
                rec.date_deadline = rec.manual_deadline_date
            else:
                rec.date_deadline = rec.automatic_deadline_date

    def _inverse_date_deadline(self):
        for rec in self:
            rec.manual_deadline_date = rec.date_deadline
