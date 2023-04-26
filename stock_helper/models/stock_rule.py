# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_pull(self, procurements):
        """You can stop the procurement run by setting a domain via context
        with the key _stop_run_pull_rule_domain
        Each given procurement's rule will be checked against this domain
        if the domain matches the rule the procurement will be stop

        By setting _stop_run_pull_move_values
        it is possible to update move values
        The value of it must be a dict where each key represents
        a key of the procurement.values which is containing move_ids
        As an example
        {"move_dest_ids": {"test": True}}
        This will write True in the field test of all moves
        which are set in procurement.values.move_dest_ids
        """
        stopping_domain = self.env.context.get("_stop_run_pull_rule_domain")
        if not stopping_domain:
            return super()._run_pull(procurements)

        stopped_move_values = self.env.context.get("_stop_run_pull_move_values", {})
        actions_to_run = []
        for procurement, rule in procurements:
            if not rule.filtered_domain(stopping_domain):
                actions_to_run.append((procurement, rule))
                continue
            for field, values in stopped_move_values.items():
                moves = procurement.values.get(field)
                if moves:
                    moves.write(values)
        return super()._run_pull(actions_to_run)
