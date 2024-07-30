# Copyright 2022 ACSONE SA/NV
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def _moves_auto_release_domain(self):
        return [
            ("product_id", "=", self.id),
            ("is_auto_release_allowed", "=", True),
        ]

    def pickings_auto_release(self):
        """Job trying to auto release pickings based on product

        It searches all* the moves auto releasable
        and triggers a delayed release available to promise for their pickings.
        """
        self.ensure_one()
        moves = self.env["stock.move"].search(self._moves_auto_release_domain())
        pickings = moves.picking_id
        if not pickings:
            return
        pickings._delay_auto_release_available_to_promise()
