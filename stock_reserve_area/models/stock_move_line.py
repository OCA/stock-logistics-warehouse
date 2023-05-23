# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _free_reservation(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        ml_to_ignore=None,
    ):
        super()._free_reservation(
            product_id,
            location_id,
            quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            ml_to_ignore=ml_to_ignore,
        )
        reserve_area_ids = self.location_id.reserve_area_ids
        for area in reserve_area_ids:
            self.env["stock.move"]._free_reservation_area(
                self.product_id, area, self.qty_done
            )
