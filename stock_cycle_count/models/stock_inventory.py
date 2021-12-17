# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

PERCENT = 100.0


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.depends("state", "line_ids")
    def _compute_inventory_accuracy(self):
        for inv in self:
            theoretical = sum(inv.line_ids.mapped(lambda x: abs(x.theoretical_qty)))
            abs_discrepancy = sum(inv.line_ids.mapped(lambda x: abs(x.discrepancy_qty)))
            if theoretical:
                inv.inventory_accuracy = max(
                    PERCENT * (theoretical - abs_discrepancy) / theoretical, 0.0
                )
            if not inv.line_ids and inv.state == "done":
                inv.inventory_accuracy = PERCENT

    cycle_count_id = fields.Many2one(
        comodel_name="stock.cycle.count",
        string="Stock Cycle Count",
        ondelete="restrict",
        readonly=True,
    )
    inventory_accuracy = fields.Float(
        string="Accuracy",
        compute="_compute_inventory_accuracy",
        digits=(3, 2),
        store=True,
        group_operator="avg",
    )

    def _update_cycle_state(self):
        for inv in self:
            if inv.cycle_count_id and inv.state == "done":
                inv.cycle_count_id.state = "done"
        return True

    def _domain_cycle_count_candidate(self):
        return [
            ("state", "=", "draft"),
            ("location_id", "in", self.location_ids.ids),
        ]

    def _link_to_planned_cycle_count(self):
        self.ensure_one()
        domain = self._domain_cycle_count_candidate()
        candidate = self.env["stock.cycle.count"].search(
            domain, limit=1, order="date_deadline asc"
        )
        # Also find inventories that do not exclude subloations but that are
        # for a bin location (no childs). This makes the attachment logic more
        # flexible and user friendly (no need to remember to tick the
        # non-standard `exclude_sublocation` field).
        if (
            candidate
            and not self.product_ids
            and (
                self.exclude_sublocation
                or (len(self.location_ids) == 1 and not self.location_ids[0].child_ids)
            )
        ):
            candidate.state = "open"
            self.write({"cycle_count_id": candidate.id, "exclude_sublocation": True})
        return True

    def action_validate(self):
        res = super(StockInventory, self).action_validate()
        self._update_cycle_state()
        return res

    def action_force_done(self):
        res = super(StockInventory, self).action_force_done()
        self._update_cycle_state()
        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not res.cycle_count_id:
            res._link_to_planned_cycle_count()
        return res

    def write(self, vals):
        for inventory in self:
            if inventory._allow_write(vals):
                raise UserError(
                    _(
                        "You cannot modify the configuration of an Inventory "
                        "Adjustment related to a Cycle Count."
                    )
                )
        return super(StockInventory, self).write(vals)

    def _allow_write(self, vals):
        return (
            self.cycle_count_id and "state" not in vals.keys() and self.state == "draft"
        )
