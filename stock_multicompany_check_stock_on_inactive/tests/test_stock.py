# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestStock(SavepointCase):
    def _set_stock_to(self, qty, location, product):
        inventory = self.env["stock.inventory"].create(
            {"location_ids": [location.id], "name": "Test starting inventory"}
        )
        self.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "location_id": location.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "product_qty": qty,
            }
        )
        inventory.action_start()
        inventory.action_validate()

    def setUp(self):
        super().setUp()

        self.warehouse_qty_zero = self.env["stock.warehouse"].create(
            {
                "name": "WH with no qty",
                "code": "TEST0",
                "lot_stock_id": [
                    6,
                    0,
                    {
                        "name": "Test Location 0",
                    },
                ],
            }
        )
        self.warehouse_qty_some_1 = self.env["stock.warehouse"].create(
            {
                "name": "WH with some qty 1",
                "code": "TEST1",
                "lot_stock_id": [
                    6,
                    0,
                    {
                        "name": "Test Location 1",
                    },
                ],
            }
        )
        self.warehouse_qty_some_2 = self.env["stock.warehouse"].create(
            {
                "name": "WH with some qty 2",
                "code": "TEST2",
                "lot_stock_id": [
                    6,
                    0,
                    {
                        "name": "Test Location 2",
                    },
                ],
            }
        )
        self.partner = self.env.ref("base.res_partner_4")
        self.product_1 = self.env.ref("product.product_product_4")
        self.product_2 = self.env.ref("product.product_product_4b")
        self.product_1.type = "product"
        self.product_2.type = "product"
        self.product_tmpl = self.product_1.product_tmpl_id
        self.location_qty_zero = self.warehouse_qty_zero.lot_stock_id
        self.location_qty_some_1 = self.warehouse_qty_some_1.lot_stock_id
        self.location_qty_some_2 = self.warehouse_qty_some_2.lot_stock_id
        self.last_move = self.env["stock.move"].search([], order="id desc")[0]
        for variant in self.product_tmpl.product_variant_ids:
            self._set_stock_to(
                0.0, self.env.ref("stock.warehouse0").lot_stock_id, variant
            )

    def test_qty_none(self):
        self.product_1.active = False
        self.product_tmpl.active = False

    def test_qty_some_1(self):
        self._set_stock_to(3.0, self.location_qty_some_1, self.product_1)
        with self.assertRaises(ValidationError) as e:
            self.product_1.active = False
        exception_msg = e.exception.name
        self.assertIn(
            "For the product [FURN_0096] Customizable Desk (CONFIG) (Steel, White):",
            exception_msg,
        )
        self.assertIn(
            "because there is stock left in at least one warehouse", exception_msg
        )
        self.assertIn("- 3.0 in warehouse WH with some qty 1", exception_msg)
        with self.assertRaises(ValidationError) as e:
            self.product_tmpl.active = False
        exception_msg = e.exception.name
        self.assertIn(
            "For the product [FURN_0096] Customizable Desk (CONFIG) (Steel, White):",
            exception_msg,
        )
        self.assertIn(
            "because there is stock left in at least one warehouse", exception_msg
        )
        self.assertIn("- 3.0 in warehouse WH with some qty 1", exception_msg)

    def test_qty_some_2(self):
        self._set_stock_to(3.0, self.location_qty_some_1, self.product_1)
        self._set_stock_to(5.0, self.location_qty_some_2, self.product_1)
        with self.assertRaises(ValidationError) as e:
            self.product_1.active = False
        exception_msg = e.exception.name
        self.assertIn(
            "For the product [FURN_0096] Customizable Desk (CONFIG) (Steel, White):",
            exception_msg,
        )
        self.assertIn("- 3.0 in warehouse WH with some qty 1", exception_msg)
        self.assertIn("- 5.0 in warehouse WH with some qty 2", exception_msg)
        with self.assertRaises(ValidationError) as e:
            self.product_tmpl.active = False
        exception_msg = e.exception.name
        self.assertIn(
            "For the product [FURN_0096] Customizable Desk (CONFIG) (Steel, White):",
            exception_msg,
        )
        self.assertIn("- 3.0 in warehouse WH with some qty 1", exception_msg)
        self.assertIn("- 5.0 in warehouse WH with some qty 2", exception_msg)

    def test_qty_some_combination(self):
        self._set_stock_to(3.0, self.location_qty_some_1, self.product_1)
        self._set_stock_to(5.0, self.location_qty_some_1, self.product_2)
        self._set_stock_to(7.0, self.location_qty_some_2, self.product_1)
        self._set_stock_to(11.0, self.location_qty_some_2, self.product_2)
        with self.assertRaises(ValidationError) as e:
            self.product_tmpl.active = False
        exception_msg = e.exception.name
        self.assertIn(
            "For the product [FURN_0097] Customizable Desk (CONFIG) (Steel, Black):",
            exception_msg,
        )
        self.assertIn("- 3.0 in warehouse WH with some qty 1", exception_msg)
        self.assertIn("- 7.0 in warehouse WH with some qty 2", exception_msg)
        self.assertIn(
            "For the product [FURN_0096] Customizable Desk (CONFIG) (Steel, White):",
            exception_msg,
        )
        self.assertIn("- 5.0 in warehouse WH with some qty 1", exception_msg)
        self.assertIn("- 11.0 in warehouse WH with some qty 2", exception_msg)
        self.assertEqual(
            exception_msg.count("\n"), 6
        )  # 1 line return + 2 qty lines per product
