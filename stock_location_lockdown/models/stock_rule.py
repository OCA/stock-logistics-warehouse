# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    is_location_blocked = fields.Boolean(
        compute="_compute_is_location_blocked",
        store=True,
        help="True if the rule's source location is outbound-blocked or its "
        "destination location is inbound-blocked. Use this for rule/route "
        "selection filtering, not the underlying location flags directly.",
    )

    @api.model
    def _is_location_blocked_depends(self):
        return (
            "location_src_id.is_outbound_blocked",
            "location_dest_id.is_inbound_blocked",
        )

    @api.depends(lambda self: self._is_location_blocked_depends())
    def _compute_is_location_blocked(self):
        for rule in self:
            rule.is_location_blocked = (
                rule.location_src_id.is_outbound_blocked
                or rule.location_dest_id.is_inbound_blocked
            )
