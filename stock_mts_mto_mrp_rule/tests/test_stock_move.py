import unittest.mock

from .common import TestCommon


class TestStockMove(TestCommon):
    def test_adjust_procure_method_make_to_stock(self):
        moves = self.run_procurement_group_and_get_stock_move(1.0)
        self.assertEqual(len(moves), 1, msg="Count records must be equal to 1")
        moves._adjust_procure_method()
        self.assertEqual(
            moves.procure_method,
            "make_to_stock",
            msg="Procure method must be equal to 'make_to_stock'",
        )

    def test_adjust_procure_method_make_to_order(self):
        moves = self.run_procurement_group_and_get_stock_move(4.0)
        self.assertEqual(len(moves), 3, msg="Count records must be equal to 3")
        moves._adjust_procure_method()
        expected_list = ["make_to_order", "make_to_order", "make_to_stock"]
        self.assertListEqual(
            moves.mapped("procure_method"), expected_list, msg="Lists must be the same"
        )

    def test_adjust_procure_method_make_to_stock_and_copy_stock_move(self):
        moves = self.run_procurement_group_and_get_stock_move(2.0)
        self.assertEqual(len(moves), 1, msg="Count records must be equal to 1")
        moves._adjust_procure_method()
        self.assertEqual(
            moves.product_uom_qty, 1, msg="Product UOM Qty must be equal to 1"
        )
        self.assertEqual(
            moves.procure_method,
            "make_to_stock",
            msg="Procure method must be equal to 'make_to_stock'",
        )
        move_copy = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("id", "!=", moves.id),
            ]
        )
        self.assertEqual(len(move_copy), 1, msg="Count records must be equal to 1")
        self.assertEqual(
            move_copy.product_uom_qty, 1, msg="Product UOM Qty must be equal to 1"
        )
        self.assertEqual(
            move_copy.procure_method,
            "make_to_order",
            msg="Procure method must be equal to 'make_to_order'",
        )

    def test_01_action_confirm_split_procurement(self):
        production = self.env["mrp.production"].create(
            {
                "name": "Test Production",
                "product_id": self.product.id,
                "product_qty": 10.0,
                "product_uom_id": self.product.uom_id.id,
                "state": "confirmed",
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom_qty": 10.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.location_src_id,
                "location_dest_id": self.location_stock.id,
                "procure_method": "make_to_stock",
                "state": "draft",
                "raw_material_production_id": production.id,
            }
        )
        move._action_confirm()
        move.invalidate_model()
        self.assertIn(move.state, ["confirmed", "assigned", "waiting"])

    def test_02_action_confirm_split_procurement(self):
        StockMove = self.env["stock.move"]
        ProcurementGroup = self.env["procurement.group"]
        mrp_production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
                "state": "confirmed",
            }
        )
        move = StockMove.create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_stock.id,
                "state": "draft",
                "procure_method": "make_to_stock",
                "raw_material_production_id": mrp_production.id,
            }
        )

        def fake_search_rule(self, *a, **kw):
            class FakeRule:
                action = "split_procurement"

                def get_mto_qty_to_order(self, *a, **kw):
                    return 5

                def _run_push(self, move):
                    # Simula el comportamiento esperado, puede devolver None
                    return None

            return FakeRule()

        with unittest.mock.patch.object(
            type(ProcurementGroup), "_search_rule", fake_search_rule
        ):
            move._action_confirm()

        self.assertIn(
            move.state, ["confirmed", "assigned", "waiting", "partially_available"]
        )

    def test_03_action_confirm_split_procurement_3(self):
        StockMove = self.env["stock.move"]
        ProcurementGroup = self.env["procurement.group"]
        mrp_production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
                "state": "confirmed",
            }
        )
        move = StockMove.create(
            {
                "name": "Test Move Confirm",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_stock.id,
                "state": "draft",
                "procure_method": "make_to_stock",
                "raw_material_production_id": mrp_production.id,
            }
        )

        def fake_search_rule(self, *a, **kw):
            class FakeRule:
                action = "split_procurement"

                def get_mto_qty_to_order(self, *a, **kw):
                    return 5

                def _run_push(self, move):
                    return None

            return FakeRule()

        with unittest.mock.patch.object(
            type(ProcurementGroup), "_search_rule", fake_search_rule
        ):
            move._action_confirm()
        moves = StockMove.search(
            [
                ("raw_material_production_id", "=", mrp_production.id),
                ("product_id", "=", self.product.id),
                ("state", "not in", ["cancel", "done"]),
            ]
        )
        self.assertGreaterEqual(len(moves), 2)
        states = set(moves.mapped("state"))
        self.assertTrue(
            states.issubset({"confirmed", "assigned", "waiting", "partially_available"})
        )
