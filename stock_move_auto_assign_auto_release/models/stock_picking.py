# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS


class StockPicking(models.Model):

    _inherit = "stock.picking"

    is_auto_release_allowed = fields.Boolean(
        compute="_compute_is_auto_release_allowed",
        search="_search_is_auto_release_allowed",
    )

    @api.model
    def _is_auto_release_allowed_depends(self):
        return ["state", "last_release_date", "printed", "release_ready"]

    @api.depends(lambda self: self._is_auto_release_allowed_depends())
    def _compute_is_auto_release_allowed(self):
        auto_releaseable_pickings = self.filtered_domain(
            self._is_auto_release_allowed_domain
        )
        auto_releaseable_picking_ids = set(auto_releaseable_pickings.ids)
        for picking in self:
            picking.is_auto_release_allowed = picking.id in auto_releaseable_picking_ids

    @property
    def _is_auto_release_allowed_domain(self):
        return [
            ("state", "not in", ("done", "cancel")),
            ("printed", "!=", True),
            ("release_ready", "=", True),
        ]

    @api.model
    def _search_is_auto_release_allowed(self, operator, value):
        if "in" in operator:
            raise ValueError(f"Invalid operator {operator}")
        negative_op = operator in NEGATIVE_TERM_OPERATORS
        is_auto_release_allowed = (value and not negative_op) or (
            not value and negative_op
        )
        domain = self._is_auto_release_allowed_domain
        if not is_auto_release_allowed:
            domain = [("id", "not in", self.search(domain).ids)]
        return domain
