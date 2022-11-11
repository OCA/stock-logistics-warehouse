# Copyright 2017-2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

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
    responsible_id = fields.Many2one(
        comodel_name="res.users",
        tracking=True,
        help="Specific responsible of Inventory Adjustment.",
    )

    def _get_default_counted_quantitites(self):
        company_id = self.env.context.get("default_company_id", self.env.company)
        return company_id.inventory_adjustment_counted_quantities or "counted"

    prefill_counted_quantity = fields.Selection(
        default=_get_default_counted_quantitites
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

    def _is_consistent_with_cycle_count(self):
        self.ensure_one()
        if (
            not self.location_ids
            or len(self.location_ids) > 1
            or self.location_ids != self.cycle_count_id.location_id
        ):
            return False, _(
                "The location in the inventory does not match with the cycle count."
            )
        if self.product_ids:
            return False, _(
                "The adjustment should be done for all products in the location."
            )
        if self.company_id != self.cycle_count_id.company_id:
            return False, _(
                "The company of the adjustment does not match with the "
                "company in the cycle count."
            )
        if not self.exclude_sublocation:
            return False, _(
                "An adjustment linked to a cycle count should exclude the sublocations."
            )
        return True, ""

    @api.constrains(
        "cycle_count_id",
        "location_ids",
        "product_ids",
        "company_id",
        "exclude_sublocation",
    )
    def _check_cycle_count_consistency(self):
        for rec in self.filtered(lambda r: r.cycle_count_id):
            is_consistent, msg = rec._is_consistent_with_cycle_count()
            if not is_consistent:
                raise ValidationError(
                    _(
                        "The Inventory Adjustment is inconsistent with the Cycle Count:\n%s"
                    )
                    % msg
                )
