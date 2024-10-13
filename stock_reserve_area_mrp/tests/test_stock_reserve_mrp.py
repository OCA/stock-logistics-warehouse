# Copyright 2023 ForgeFLow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_reserve_area.tests.test_stock_reserve import TestStockReserveArea


class TestStockReserveAreaMrp(TestStockReserveArea):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manufacture_product = cls.env["product.product"].create(
            {"name": "Test Product Manufacture", "type": "product"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.manufacture_product.product_tmpl_id.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.product.id, "product_qty": 1}),
                ],
            }
        )

    def test_reservation_area_mrp(self):
        """We create a MO where the product won't go out of the reserve area.
        The product won't be reserved in the area."""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.manufacture_product.id,
                "product_uom_id": self.manufacture_product.uom_id.id,
                "bom_id": self.bom.id,
                "location_src_id": self.wh1_stock1.id,
                "product_qty": 1,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test",
                "location_id": self.wh1_stock1.id,
                "location_dest_id": mo.production_location_id.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1.0,
            }
        )
        mo.move_raw_ids = move
        self.assertEqual(mo.reserve_area_id, self.reserve_area1)

        mo.action_confirm()
        mo.action_assign()
        self.assertEqual(
            mo.move_raw_ids.area_reserved_availability,
            1,
            "1 units should have been "
            "reserved in the Reserve Area"
            "for this product.",
        )
        mo.move_raw_ids.quantity_done = 1
        mo.qty_producing = 1
        mo.button_mark_done()
        self.assertEqual(
            mo.move_raw_ids[0].area_reserved_availability,
            0,
            "There shouldn't be any reserved units in the area for this move.",
        )
