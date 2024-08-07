# Copyright 2022 ACSONE SA/NV
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS

from odoo.addons.queue_job.job import identity_exact


class StockMove(models.Model):

    _inherit = "stock.move"

    is_auto_release_allowed = fields.Boolean(
        compute="_compute_is_auto_release_allowed",
        search="_search_is_auto_release_allowed",
    )

    @api.model
    def _is_auto_release_allowed_depends(self):
        return [
            "state",
            "need_release",
            "ordered_available_to_promise_uom_qty",
            "picking_id.is_auto_release_allowed",
        ]

    @api.depends(lambda self: self._is_auto_release_allowed_depends())
    def _compute_is_auto_release_allowed(self):
        auto_releaseable_moves = self.filtered_domain(
            self._is_auto_release_allowed_domain
        )
        auto_releaseable_move_ids = set(auto_releaseable_moves.ids)
        for move in self:
            move.is_auto_release_allowed = move.id in auto_releaseable_move_ids

    @property
    def _is_auto_release_allowed_domain(self):
        return [
            ("state", "not in", ("done", "cancel")),
            ("need_release", "=", True),
            ("ordered_available_to_promise_uom_qty", ">", 0),
            ("picking_id.is_auto_release_allowed", "=", True),
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

    def _enqueue_auto_assign(self, product, locations, **job_options):
        job = super()._enqueue_auto_assign(product, locations, **job_options)
        job_options = job_options.copy()
        job_options.setdefault(
            "description",
            _('Try releasing "{}" for quantities added in: {}').format(
                product.display_name, ", ".join(locations.mapped("name"))
            ),
        )
        job_options.setdefault("identity_key", identity_exact)
        delayable = product.delayable(**job_options)
        release_job = delayable.pickings_auto_release()
        job.on_done(release_job)
        return job
