# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_pull(self, procurements):
        actions_to_run = []

        for procurement, rule in procurements:
            if (
                not self.env.context.get("_rule_no_available_defer")
                and rule.route_id.available_to_promise_defer_pull
                # We still want to create the first part of the chain
                and not rule.picking_type_id.code == "outgoing"
            ):
                moves = procurement.values.get("move_dest_ids")
                # Track the moves that needs to have their pull rule
                # done. Before the 'pull' is done, we don't know the
                # which route is chosen. We update the destination
                # move (ie. the outgoing) when the current route
                # defers the pull rules and return so we don't create
                # the next move of the chain (pick or pack).
                if moves:
                    moves.write({"need_release": True})
            else:
                actions_to_run.append((procurement, rule))

        super()._run_pull(actions_to_run)
        # use first of list of ids and browse it for performance
        move_ids = [
            move.id
            for move in procurement.values.get("move_dest_ids", [])
            for procurement, _rule in actions_to_run
        ]
        if move_ids:
            moves = self.env["stock.move"].browse(move_ids)
            moves.filtered(lambda r: r.need_release).write({"need_release": False})
        return True


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def run_defer(self, procurements):
        actions_to_run = []
        for procurement in procurements:
            values = procurement.values
            values.setdefault("company_id", self.env.company)
            values.setdefault("priority", "1")
            values.setdefault("date_planned", fields.Datetime.now())
            rule = self._get_rule(
                procurement.product_id, procurement.location_id, procurement.values
            )
            if rule.action in ("pull", "pull_push"):
                actions_to_run.append((procurement, rule))

        if actions_to_run:
            rule.with_context(_rule_no_available_defer=True)._run_pull(actions_to_run)
        return True
