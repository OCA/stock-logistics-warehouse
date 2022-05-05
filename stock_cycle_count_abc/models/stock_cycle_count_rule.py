# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class StockCycleCountRule(models.Model):
    _inherit = "stock.cycle.count.rule"

    @api.model
    def _selection_rule_types(self):
        res = super()._selection_rule_types()
        res.append(("abc", _("ABC Analysis")))
        return res

    frequency = fields.Selection(
        [
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
        ],
        "Frequency",
    )

    def compute_rule(self, locs):
        if self.rule_type == "abc":
            proposed_cycle_counts = self._compute_rule_abc(locs)
            return proposed_cycle_counts
        return super().compute_rule(locs)

    @api.model
    def _compute_rule_abc(self, locs):
        cycle_counts = []
        stock_inventory = self.env["stock.inventory"].search(
            [
                ("state", "in", ["confirm", "done", "draft"]),
            ],
            order="date desc",
        )
        latest_inventory_date = False
        for loc in locs:
            latest_inventory = stock_inventory.filtered(
                lambda r: loc.id in r.location_ids.ids
            )
            if latest_inventory:
                latest_inventory_date = latest_inventory[0].date
            if latest_inventory_date:
                if self.frequency == "daily":
                    next_date = datetime.today()
                elif self.frequency == "weekly":
                    next_date = fields.Datetime.from_string(
                        latest_inventory_date
                    ) + timedelta(days=7)
                elif self.frequency == "monthly":
                    next_date = fields.Datetime.from_string(
                        latest_inventory_date
                    ) + timedelta(days=30)
                elif self.frequency == "quarterly":
                    next_date = fields.Datetime.from_string(
                        latest_inventory_date
                    ) + relativedelta(months=3)
            else:
                next_date = datetime.today()
            cycle_count = self._propose_cycle_count(next_date, loc)
            cycle_counts.append(cycle_count)
        return cycle_counts
