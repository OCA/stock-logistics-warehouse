# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models

from odoo.addons.queue_job.job import job


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

    @job(default_channel="root.stock_auto_assign")
    def moves_auto_assign(self, locations):
        """Try to reserve moves based on product and locations

        When a product has been added to a location, it searches all*
        the moves with a source equal or above this location and try
        to reserve them.

        * all the moves that would make sense to reserve, so no chained
        moves, no MTO, ...
        """
        self.ensure_one()
        moves = self.env["stock.move"].search(self._moves_auto_assign_domain(locations))
        moves._action_assign()
