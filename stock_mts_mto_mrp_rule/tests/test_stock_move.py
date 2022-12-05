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
