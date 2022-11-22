# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def _moves_auto_release_domain(self):
        return [
            ("product_id", "=", self.id),
            ("is_auto_release_allowed", "=", True),
        ]

    def moves_auto_release(self):
        """Job trying to auto release moves based on product

        It searches all* the moves auto releasable and trigger the release
        available to promise process.
        """
        self.ensure_one()
        moves = self.env["stock.move"].search(self._moves_auto_release_domain())
        pickings = moves.picking_id
        if not pickings:
            return
        self._lock_pickings_or_retry(pickings)
        moves.release_available_to_promise()
