# Copyright 2020-2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.stock_helper.tests.common import StockHelperCommonCase


class StockHelperDeliveryCommonCase(StockHelperCommonCase):
    def _create_move(self, product, src_location, dst_location, **values):
        Move = self.env["stock.move"]
        # simulate create + onchange
        move = Move.new(
            {
                "product_id": product.id,
                "location_id": src_location.id,
                "location_dest_id": dst_location.id,
            }
        )
        move.onchange_product_id()
        move_values = move._convert_to_write(move._cache)
        move_values.update(**values)
        return Move.create(move_values)
