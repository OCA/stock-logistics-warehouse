# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_reserve_area_available_quantity(self, product_id, reserve_area_id):
        self = self.sudo()
        quants = self._gather_reserve_area(product_id, reserve_area_id)
        rounding = product_id.uom_id.rounding
        sum_qty = (
            self.read_group([("id", "in", quants.ids)], ["quantity"], [])[0]["quantity"]
            or 0
        )
        sum_area_reserved_qty = (
            self.env["stock.move.reserve.area.line"].read_group(
                [
                    ("reserve_area_id", "=", reserve_area_id.id),
                    ("product_id", "=", product_id.id),
                ],
                ["reserved_availability"],
                [],
            )[0]["reserved_availability"]
            or 0
        )
        available_quantity = float(sum_qty) - float(sum_area_reserved_qty)
        return (
            available_quantity
            if float_compare(available_quantity, 0.0, precision_rounding=rounding)
            >= 0.0
            else 0.0
        )

    def _gather_reserve_area(self, product_id, reserve_area_id):
        self.env["stock.quant"].flush(["available_quantity"])
        quant_ids = []
        for location_id in reserve_area_id.location_ids:
            if reserve_area_id.is_location_in_area(location_id):
                quant_ids += self._gather(product_id, location_id).ids
        return self.browse(quant_ids)
