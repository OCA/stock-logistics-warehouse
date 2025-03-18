# Copyright 2017-2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

PERCENT = 100.0


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    prefill_counted_quantity = fields.Selection(
        string="Counted Quantities",
        help="Allows to start with a pre-filled counted quantity for each lines or "
        "with all counted quantities set to zero.",
        default="counted",
        selection=[
            ("counted", "Default to stock on hand"),
            ("zero", "Default to zero"),
        ],
    )
    cycle_count_id = fields.Many2one(
        comodel_name="stock.cycle.count",
        string="Stock Cycle Count",
        ondelete="restrict",
        readonly=True,
    )
    inventory_accuracy = fields.Float(
        string="Accuracy",
        digits=(3, 2),
        store=True,
        group_operator="avg",
        default=False,
    )
    responsible_id = fields.Many2one(
        tracking=True,
        compute="_compute_responsible_id",
        inverse="_inverse_responsible_id",
        store=True,
        readonly=False,
    )

    @api.depends("cycle_count_id.responsible_id")
    def _compute_responsible_id(self):
        for inv in self:
            if inv.cycle_count_id:
                inv.responsible_id = inv.cycle_count_id.responsible_id
                inv.stock_quant_ids.write(
                    {"user_id": inv.cycle_count_id.responsible_id}
                )

    def _inverse_responsible_id(self):
        for inv in self:
            if inv.cycle_count_id and inv.responsible_id:
                inv.cycle_count_id.responsible_id = inv.responsible_id

    def write(self, vals):
        result = super().write(vals)
        if "responsible_id" in vals:
            if not self.env.context.get("no_propagate"):
                if (
                    self.cycle_count_id
                    and self.cycle_count_id.responsible_id.id != vals["responsible_id"]
                ):
                    self.cycle_count_id.with_context(no_propagate=True).write(
                        {"responsible_id": vals["responsible_id"]}
                    )
            for quant in self.mapped("stock_quant_ids"):
                if quant.user_id.id != vals["responsible_id"]:
                    quant.write({"user_id": vals["responsible_id"]})
        return result

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

    def _calculate_inventory_accuracy(self):
        for inv in self:
            accuracy = 100
            sum_line_accuracy = 0
            sum_theoretical_qty = 0
            if inv.stock_move_ids:
                for line in inv.stock_move_ids:
                    sum_line_accuracy += line.theoretical_qty * line.line_accuracy
                    sum_theoretical_qty += line.theoretical_qty
                if sum_theoretical_qty != 0:
                    accuracy = (sum_line_accuracy / sum_theoretical_qty) * 100
                else:
                    accuracy = 0
            inv.update(
                {
                    "inventory_accuracy": accuracy,
                }
            )
        return False

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

    def action_state_to_done(self):
        res = super().action_state_to_done()
        self._calculate_inventory_accuracy()
        self._update_cycle_state()
        return res

    def action_force_done(self):
        res = super().action_force_done()
        self._calculate_inventory_accuracy()
        self._update_cycle_state()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        inventories = super().create(vals_list)
        for inv in inventories:
            if not inv.cycle_count_id:
                inv._link_to_planned_cycle_count()
        return inventories

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
                        "The Inventory Adjustment is inconsistent "
                        "with the Cycle Count:\n%(message)s",
                        message=msg,
                    )
                )

    def action_state_to_in_progress(self):
        res = super().action_state_to_in_progress()
        self.prefill_counted_quantity = (
            self.company_id.inventory_adjustment_counted_quantities
        )
        if self.prefill_counted_quantity == "zero":
            self.stock_quant_ids.write({"inventory_quantity": 0})
        elif self.prefill_counted_quantity == "counted":
            for quant in self.stock_quant_ids:
                quant.write({"inventory_quantity": quant.quantity})
        return res
