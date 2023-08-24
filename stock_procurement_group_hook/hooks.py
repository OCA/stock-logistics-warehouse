# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
from collections import defaultdict

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.stock.models.stock_rule import ProcurementException, ProcurementGroup

_logger = logging.getLogger(__name__)


def post_load_hook():

    # Changes done to the original method are highlighted with the comments
    # "START/END OF CHANGES"
    @api.model
    def run_new(self, procurements, raise_user_error=True):
        def raise_exception(procurement_errors):
            if raise_user_error:
                dummy, errors = zip(*procurement_errors)
                raise UserError("\n".join(errors))
            else:
                raise ProcurementException(procurement_errors)

        actions_to_run = defaultdict(list)
        procurement_errors = []
        for procurement in procurements:
            procurement.values.setdefault(
                "company_id", procurement.location_id.company_id
            )
            procurement.values.setdefault("priority", "0")
            procurement.values.setdefault("date_planned", fields.Datetime.now())
            # START OF CHANGES
            if self._skip_procurement(procurement):
                # END OF CHANGES
                continue
            rule = self._get_rule(
                procurement.product_id, procurement.location_id, procurement.values
            )
            if not rule:
                error = _(
                    'No rule has been found to replenish "%(pidn)s" in "%(lidn)s".\n'
                    "Verify the routes configuration on the product."
                ) % {
                    "pidn": procurement.product_id.display_name,
                    "lidn": procurement.location_id.display_name,
                }
                procurement_errors.append((procurement, error))
            else:
                action = "pull" if rule.action == "pull_push" else rule.action
                actions_to_run[action].append((procurement, rule))

        if procurement_errors:
            raise_exception(procurement_errors)

        for action, procurements in actions_to_run.items():
            if hasattr(self.env["stock.rule"], "_run_%s" % action):
                try:
                    getattr(self.env["stock.rule"], "_run_%s" % action)(procurements)
                except ProcurementException as e:
                    procurement_errors += e.procurement_exceptions
            else:
                _logger.error(
                    "The method _run_%s doesn't exist on the procurement rules" % action
                )

        if procurement_errors:
            raise_exception(procurement_errors)
        return True

    if not hasattr(ProcurementGroup, "run_original"):
        ProcurementGroup.run_original = ProcurementGroup.run
    ProcurementGroup.run = run_new
