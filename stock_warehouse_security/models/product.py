# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _get_domain_locations_new(self, location_ids):
        if self.env.user.warehouse_ids:
            location_ids = set(
                self.env["stock.location"]
                .search(
                    [
                        ("warehouse_id", "in", self.env.user.warehouse_ids.ids),
                        ("id", "in", list(location_ids)),
                    ]
                )
                .ids
            )
        return super()._get_domain_locations_new(location_ids)
