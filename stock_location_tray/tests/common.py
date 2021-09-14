# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class LocationTrayTypeCase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env.ref("product.product_delivery_02")
        cls.tray_location = cls.env.ref("stock_location_tray.stock_location_tray_demo")
        cls.tray_type_small_8x = cls.env.ref(
            "stock_location_tray.stock_location_tray_type_small_8x"
        )
        cls.tray_type_small_32x = cls.env.ref(
            "stock_location_tray.stock_location_tray_type_small_32x"
        )

    def _create_tray_z(self, tray_type=None):
        tray_type = tray_type or self.tray_type_small_8x
        tray_z = self.env["stock.location"].create(
            {
                "name": "Tray Z",
                "location_id": self.stock_location.id,
                "usage": "internal",
                "tray_type_id": tray_type.id,
            }
        )
        return tray_z

    def _cell_for(self, tray, x=1, y=1):
        cell = self.env["stock.location"].search(
            [("location_id", "=", tray.id), ("posx", "=", x), ("posy", "=", y)]
        )
        self.assertEqual(
            len(cell), 1, "Cell x{}y{} not found for {}".format(x, y, tray.name)
        )
        return cell

    def _update_quantity_in_cell(self, cell, product, quantity):
        self.env["stock.quant"]._update_available_quantity(product, cell, quantity)
