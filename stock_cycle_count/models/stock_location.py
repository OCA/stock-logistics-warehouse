# Copyright 2017-18 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

from odoo import fields, models, tools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

try:
    from statistics import mean

    STATS_PATH = tools.find_in_path("statistics")
except (ImportError, IOError) as err:
    _logger.debug(err)


class StockLocation(models.Model):
    _inherit = "stock.location"

    zero_confirmation_disabled = fields.Boolean(
        string="Disable Zero Confirmations",
        help="Define whether this location will trigger a zero-confirmation "
        "validation when a rule for its warehouse is defined to perform "
        "zero-confirmations.",
    )
    cycle_count_disabled = fields.Boolean(
        string="Exclude from Cycle Count",
        help="Define whether the location is going to be cycle counted.",
    )
    qty_variance_inventory_threshold = fields.Float(
        string="Acceptable Inventory Quantity Variance Threshold"
    )
    loc_accuracy = fields.Float(
        string="Inventory Accuracy", compute="_compute_loc_accuracy", digits=(3, 2)
    )

    def _compute_loc_accuracy(self):
        history = self.env["stock.inventory"].search(
            [("location_ids", "in", self.ids), ("state", "=", "done")],
            order="write_date desc",
        )
        for rec in self:
            loc_history = history.filtered_domain([("location_ids", "in", rec.id)])
            if loc_history:
                wh = rec.warehouse_id
                if (
                    wh.counts_for_accuracy_qty
                    and len(loc_history) > wh.counts_for_accuracy_qty
                ):
                    rec.loc_accuracy = mean(
                        loc_history[: wh.counts_for_accuracy_qty].mapped(
                            "inventory_accuracy"
                        )
                    )
                else:
                    rec.loc_accuracy = mean(loc_history.mapped("inventory_accuracy"))
            else:
                rec.loc_accuracy = 0

    def _get_zero_confirmation_domain(self):
        self.ensure_one()
        domain = [("location_id", "=", self.id), ("quantity", ">", 0.0)]
        return domain

    def check_zero_confirmation(self):
        rule_model = self.env["stock.cycle.count.rule"]
        warehouse_ids = self.mapped("warehouse_id.id")
        zero_rules = rule_model.search(
            [("rule_type", "=", "zero"), ("warehouse_ids", "in", warehouse_ids)]
        )
        warehouse_to_rules = {rule.warehouse_ids.id: rule for rule in zero_rules}

        for rec in self:
            if not rec.zero_confirmation_disabled:
                wh = rec.warehouse_id
                zero_rule = warehouse_to_rules.get(wh.id)
                if zero_rule:
                    quants = self.env["stock.quant"].search(
                        rec._get_zero_confirmation_domain()
                    )
                    if not quants:
                        rec.create_zero_confirmation_cycle_count()

    def create_zero_confirmation_cycle_count(self):
        self.ensure_one()
        date = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        wh_id = self.warehouse_id.id
        date_horizon = self.warehouse_id.get_horizon_date().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT
        )
        counts_planned = self.env["stock.cycle.count"].search(
            [
                ("date_deadline", "<", date_horizon),
                ("state", "=", "draft"),
                ("location_id", "=", self.id),
            ]
        )
        if counts_planned:
            counts_planned.write({"state": "cancelled"})
        rule = self.env["stock.cycle.count.rule"].search(
            [("rule_type", "=", "zero"), ("warehouse_ids", "=", wh_id)]
        )
        self.env["stock.cycle.count"].create(
            {
                "automatic_deadline_date": date,
                "location_id": self.id,
                "cycle_count_rule_id": rule.id,
                "state": "draft",
            }
        )
        return True

    def action_accuracy_stats(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_cycle_count.act_accuracy_stats"
        )
        new_domain = action["domain"][:-1] + ", ('location_ids', 'in', active_ids)]"
        action["domain"] = new_domain
        return action
