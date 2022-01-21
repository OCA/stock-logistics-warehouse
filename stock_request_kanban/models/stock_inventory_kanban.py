# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class StockInventoryKanban(models.Model):
    _name = "stock.inventory.kanban"
    _description = "Inventory for Kanban"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        readonly=True, states={"draft": [("readonly", False)]}, copy=False
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("finished", "Finished"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        readonly=True,
        copy=False,
        tracking=True,
    )
    warehouse_ids = fields.Many2many(
        "stock.warehouse",
        string="Warehouse",
        ondelete="cascade",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    location_ids = fields.Many2many(
        "stock.location",
        string="Location",
        domain=[("usage", "in", ["internal", "transit"])],
        ondelete="cascade",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        domain=[("type", "in", ["product", "consu"])],
        ondelete="cascade",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    kanban_ids = fields.Many2many(
        "stock.request.kanban",
        relation="stock_inventory_kanban_kanban",
        readonly=True,
        copy=False,
    )
    scanned_kanban_ids = fields.Many2many(
        "stock.request.kanban",
        relation="stock_inventory_kanban_scanned_kanban",
        readonly=True,
        copy=False,
    )
    missing_kanban_ids = fields.Many2many(
        "stock.request.kanban", readonly=True, compute="_compute_missing_kanban"
    )

    count_missing_kanbans = fields.Integer(
        "Missing Kanbans", readonly=True, compute="_compute_missing_kanban"
    )

    @api.depends("kanban_ids", "scanned_kanban_ids")
    def _compute_missing_kanban(self):
        for rec in self:
            rec.missing_kanban_ids = rec.kanban_ids.filtered(
                lambda r: r.id not in rec.scanned_kanban_ids.ids
            )
            rec.count_missing_kanbans = len(rec.missing_kanban_ids)

    def _get_inventory_kanban_domain(self):
        domain = []
        if self.warehouse_ids:
            domain = expression.AND(
                (domain, [("warehouse_id", "in", self.warehouse_ids.ids)])
            )
        if self.product_ids:
            domain = expression.AND(
                (domain, [("product_id", "in", self.product_ids.ids)])
            )
        if self.location_ids:
            domain = expression.AND(
                (domain, [("location_id", "in", self.location_ids.ids)])
            )
        return domain

    def _start_inventory_values(self):
        return {"state": "in_progress"}

    def _finish_inventory_values(self):
        return {"state": "finished"}

    def _close_inventory_values(self):
        return {"state": "closed"}

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "stock.inventory.kanban"
            )
        return super().create(vals)

    def calculate_kanbans(self):
        for rec in self:
            if rec.state == "draft":
                rec.kanban_ids = self.env["stock.request.kanban"].search(
                    rec._get_inventory_kanban_domain()
                )

    def start_inventory(self):
        self.calculate_kanbans()
        self.write(self._start_inventory_values())

    def finish_inventory(self):
        self.write(self._finish_inventory_values())

    def close_inventory(self):
        self.write(self._close_inventory_values())

    def print_missing_kanbans(self):
        """Print the missing kanban cards in order to restore them"""
        self.ensure_one()
        return self.env.ref("stock_request_kanban.action_report_kanban").report_action(
            self.missing_kanban_ids
        )

    def _cancel_inventory_values(self):
        return {"state": "cancelled"}

    def cancel(self):
        self.write(self._cancel_inventory_values())

    def _to_draft_inventory_values(self):
        return {
            "state": "draft",
            "kanban_ids": [(5, 0)],
            "scanned_kanban_ids": [(5, 0)],
        }

    def to_draft(self):
        self.write(self._to_draft_inventory_values())
