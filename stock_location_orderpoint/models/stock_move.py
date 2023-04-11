# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models

from odoo.addons.queue_job.job import identity_exact


class StockMove(models.Model):
    _inherit = "stock.move"

    location_orderpoint_id = fields.Many2one(
        "stock.location.orderpoint", "Stock location orderpoint"
    )

    def _prepare_location_orderpoint_replenishment(self, location_field, domain):
        locations_products = {}
        for move in self:
            if not move.filtered_domain(domain):
                continue
            location = getattr(move, location_field)
            locations_products.setdefault(location, self.env["product.product"])
            locations_products[location] |= move.product_id

        for location, products in locations_products.items():
            for product in products:
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
            _("Try to replenish quantities for location {} and product {}").format(
                location.display_name, product.display_name
            ),
        )
        # do not enqueue 2 jobs for the same location and product set
        job_options.setdefault("identity_key", identity_exact)
        delayable = self.env["stock.location.orderpoint"].delayable(**job_options)
        job = delayable.run_auto_replenishment(
            product,
            location,
            location_field == "location_id" and location_field or "location_src_id",
        )
        return job

    def _action_confirm(self, *args, **kwargs):
        """This triggers the replenishment for new moves which are waiting for stock"""
        moves = super()._action_confirm(*args, **kwargs)
        moves._prepare_location_orderpoint_replenishment(
            "location_id",
            self.env["stock.location.orderpoint"]._get_waiting_move_domain(),
        )
        return moves

    def _action_done(self, *args, **kwargs):
        """
        This triggers the replenishment for waiting moves
        when the stock increases on a source location of an orderpoint
        """
        moves = super()._action_done(*args, **kwargs)
        moves._prepare_location_orderpoint_replenishment(
            "location_dest_id",
            [
                ("move_dest_ids", "=", False),
                ("procure_method", "=", "make_to_stock"),
            ],
        )
        return moves
