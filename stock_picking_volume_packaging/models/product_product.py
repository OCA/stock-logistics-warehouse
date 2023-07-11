# Copyright 2020-2022 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_volume_for_qty(self, qty, from_uom=None):
        self.ensure_one()
        if not self.packaging_ids.filtered("volume"):
            return super()._get_volume_for_qty(qty, from_uom)
        qty = from_uom and from_uom._compute_quantity(qty, self.uom_id) or qty
        packagings_with_volume = self.with_context(
            _packaging_filter=lambda p: p.volume
        ).product_qty_by_packaging(qty)
        volume = 0
        for packaging_info in packagings_with_volume:
            if packaging_info.get("is_unit"):
                pack_volume = self.volume
            else:
                packaging = self.env["product.packaging"].browse(packaging_info["id"])
                pack_volume = packaging.volume

            volume += pack_volume * packaging_info["qty"]
        return volume
