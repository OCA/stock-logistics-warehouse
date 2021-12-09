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

    def _compute_loc_accuracy(self):
        for rec in self:
            history = self.env["stock.inventory"].search(
                [("location_ids", "in", rec.id), ("state", "=", "done")],
                order="write_date desc",
            )
            if history:
                wh = rec.get_warehouse()
                if (
                    wh.counts_for_accuracy_qty
                    and len(history) > wh.counts_for_accuracy_qty
                ):
                    rec.loc_accuracy = mean(
                        history[: wh.counts_for_accuracy_qty].mapped(
                            "inventory_accuracy"
                        )
                    )
                else:
                    rec.loc_accuracy = mean(history.mapped("inventory_accuracy"))
            else:
                rec.loc_accuracy = 0

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

    def _get_zero_confirmation_domain(self):
        self.ensure_one()
        domain = [("location_id", "=", self.id), ("quantity", ">", 0.0)]
        return domain

    def check_zero_confirmation(self):
        for rec in self:
            if not rec.zero_confirmation_disabled:
                wh = rec.get_warehouse()
                rule_model = self.env["stock.cycle.count.rule"]
                zero_rule = rule_model.search(
                    [("rule_type", "=", "zero"), ("warehouse_ids", "=", wh.id)]
                )
                if zero_rule:
                    quants = self.env["stock.quant"].search(
                        rec._get_zero_confirmation_domain()
                    )
                    if not quants:
                        rec.create_zero_confirmation_cycle_count()

    def create_zero_confirmation_cycle_count(self):
        self.ensure_one()
        date = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        wh_id = self.get_warehouse().id
        date_horizon = (
            self.get_warehouse()
            .get_horizon_date()
            .strftime(DEFAULT_SERVER_DATETIME_FORMAT)
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
                "date_deadline": date,
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
