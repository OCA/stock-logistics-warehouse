# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, fields, models
from odoo.tools import ormcache

from odoo.addons.queue_job.job import identity_exact


class StockMove(models.Model):
    _inherit = "stock.move"

    location_orderpoint_id = fields.Many2one(
        "stock.location.orderpoint", "Stock location orderpoint", index=True
    )

    @ormcache("self", "product")
    def _get_location_orderpoint_replenishment_date(self, product):
        return min(
            self.filtered(lambda move: move.product_id == product).mapped("date")
        )

    def _prepare_auto_replenishment_for_waiting_moves(self):
        self._prepare_auto_replenishment(
            "location_id",
            self.env["stock.location.orderpoint"]._get_waiting_move_domain(),
        )

    def _prepare_auto_replenishment_for_done_moves(self):
        self._prepare_auto_replenishment(
            "location_dest_id",
            [
                ("move_dest_ids", "=", False),
                ("procure_method", "=", "make_to_stock"),
                ("state", "=", "done"),
            ],
        )

    def _prepare_auto_replenishment(self, location_field, domain):
        if self.env.context.get("skip_auto_replenishment"):
            return
        locations_products = defaultdict(set)
        location_ids = set()
        product_obj = self.env["product.product"]
        for move in self.filtered_domain(domain):
            location = getattr(move, location_field)
            locations_products[location].add(move.product_id.id)
            location_ids.add(location.id)
        # Map the the move's location field
        # to the correspoding stock.location.orderpoint's location field
        location_field = (
            location_field == "location_id" and location_field or "location_src_id"
        )
        orderpoints = self.env["stock.location.orderpoint"]._get_orderpoints(
            "auto", list(location_ids), location_field
        )
        for location, products in locations_products.items():
            if not orderpoints._is_location_parent_of(location, location_field):
                continue
            for product in product_obj.browse(products):
                self._enqueue_auto_replenishment(
                    location, product, location_field
                ).delay()

    def _enqueue_auto_replenishment(
        self, location, product, location_field, **job_options
    ):
        """Enqueue a job stock.location.orderpoint.moves_auto_replenishment()

        Can be extended to pass different options to the job (priority, ...).
        The usage of `.setdefault` allows to override the options set by default.

        return: a `Job` instance
        """
        job_options = job_options.copy()
        job_options.setdefault(
            "description",
            _("Try to replenish quantities {} location {} for product {}").format(
                location_field == "location_id" and _("in") or _("from"),
                location.display_name,
                product.display_name,
            ),
        )
        # do not enqueue 2 jobs for the same location and product set
        job_options.setdefault("identity_key", identity_exact)
        delayable = self.env["stock.location.orderpoint"].delayable(**job_options)
        job = delayable.run_auto_replenishment(
            product,
            location,
            location_field,
        )
        return job

    def _action_assign(self, *args, **kwargs):
        """This triggers the replenishment for new moves which are waiting for stock"""
        res = super()._action_assign(*args, **kwargs)
        self._prepare_auto_replenishment_for_waiting_moves()
        return res

    def _action_done(self, *args, **kwargs):
        """
        This triggers the replenishment for waiting moves
        when the stock increases on a source location of an orderpoint
        """
        moves = super()._action_done(*args, **kwargs)
        moves._prepare_auto_replenishment_for_done_moves()
        return moves
