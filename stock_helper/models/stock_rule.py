# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_pull(self, procurements):
        """Do not run the pull on procurements where the given domain
        is matching the procurement's rule. The domain is will be given
        via context named _run_pull_stop_rule_domain.

        Write values to stopped moves by setting a context value
        called _run_pull_stop_move_values.
        The value must be a dict where the keys are representing a key
        which is used in the procurement.values and containing moves.
        As an example
        {"move_dest_ids": {"test": True}}
        This will write True in the field test of all moves
        which are set in procurement.values.move_dest_ids
        """
        stopping_domain = self.env.context.get("_run_pull_stop_rule_domain")
        if not stopping_domain:
            return super()._run_pull(procurements)

        stopped_move_values = self.env.context.get("_run_pull_stop_move_values", {})
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
