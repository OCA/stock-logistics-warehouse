# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import psycopg2

from odoo import models

from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _moves_auto_assign_domain(self, locations):
        return [
            ("product_id", "=", self.id),
            ("location_id", "parent_of", locations.ids),
            ("state", "in", ("confirmed", "partially_available")),
            # useless to try reserving a move that waits on another move
            # or is MTO
            ("move_orig_ids", "=", False),
            ("procure_method", "=", "make_to_stock"),
            # Do not filter on product_id.type by default because it uses an
            # additional query on product_product and product_template.
            # StockMove._prepare_auto_assign() already filtered out
            # non-stockable products and # `_action_assign()` would filter them
            # out anyway.
        ]

    def moves_auto_assign(self, locations):
        """Job trying to reserve moves based on product and locations

        When a product has been added to a location, it searches all*
        the moves with a source equal or above this location and try
        to reserve them.

        * all the moves that would make sense to reserve, so no chained
        moves, no MTO, ...
        """
        self.ensure_one()
        moves = self.env["stock.move"].search(self._moves_auto_assign_domain(locations))
        pickings = moves.picking_id
        if not pickings:
            return
        try:
            self.env.cr.execute(
                "SELECT id FROM stock_picking WHERE id IN %s FOR UPDATE NOWAIT",
                (tuple(pickings.ids),),
            )
        except psycopg2.OperationalError as err:
            if err.pgcode == "55P03":  # could not obtain the lock
                _logger.debug(
                    "Another job is already auto-assigning moves and acquired a"
                    " lock on one or some of stock.picking%s, retry later.",
                    tuple(pickings.ids),
                )
                raise RetryableJobError(
                    "Could not obtain lock on transfers, will retry.", ignore_retry=True
                ) from err
            raise
        moves._action_assign()
