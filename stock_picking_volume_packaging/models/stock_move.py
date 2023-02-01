# Copyright 2020-2022 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_volume_for_qty(self, qty):
        self.ensure_one()
        product = self.product_id
        if not product.packaging_ids.filtered("volume"):
            return super()._get_volume_for_qty(qty=qty)
        packagings_with_volume = product.with_context(
            _packaging_filter=lambda p: p.volume
        ).product_qty_by_packaging(qty)
        volume = 0
        for packaging_info in packagings_with_volume:
            if packaging_info.get("is_unit"):
                pack_volume = product.volume
            else:
                packaging = self.env["product.packaging"].browse(packaging_info["id"])
                pack_volume = packaging.volume

            volume += pack_volume * packaging_info["qty"]
        return volume
