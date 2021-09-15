# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.addons.stock_packaging_calculator.tests.common import TestCommon

# from odoo.addons.stock_packaging_calculator.tests.utils import make_pkg_values


class TestStock(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ref = cls.env.ref
        cls.stock_location = ref("stock.stock_location_stock")
        cls.sub_location = cls.env["stock.location"].create(
            {"name": "Sub", "location_id": cls.stock_location.id}
        )
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.picking_type = cls.wh.out_type_id
        cls.product_a.type = "product"
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_a, cls.stock_location, 2825
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": "test",
                "product_id": cls.product_a.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.sub_location.id,
                "product_uom": cls.product_a.uom_id.id,
                "product_uom_qty": 2825,
                "state": "waiting",
                "picking_type_id": cls.picking_type.id,
            }
        )
        cls.move._assign_picking()
        cls.move._action_assign()
        cls.move_line = cls.move.move_line_ids[0]
        cls.move_line.product_uom_qty = 1470
        cls.quant = cls.env["stock.quant"].create(
            {
                "location_id": cls.stock_location.id,
                "product_id": cls.product_a.id,
                "quantity": 3190.0,
            }
        )

    def test_move(self):
        self.assertEqual(
            self.move.product_qty_by_packaging_display,
            "1 Pallet,\xa04 Big Box,\xa025 Units",
        )

    def test_move_line(self):
        self.assertEqual(
            self.move_line.product_qty_by_packaging_display,
            "7 Big Box,\xa01 Box,\xa020 Units",
        )

    def test_quant(self):
        self.assertEqual(
            self.quant.product_qty_by_packaging_display,
            "1 Pallet,\xa05 Big Box,\xa03 Box,\xa040 Units",
        )
