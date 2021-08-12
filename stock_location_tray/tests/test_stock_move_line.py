# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import LocationTrayTypeCase


class TestStockMoveLine(LocationTrayTypeCase):
    def create_stock_move(self):
        StockMove = self.env["stock.move"]
        StockMoveLine = self.env["stock.move.line"]
        cell1 = self._cell_for(self.tray_location, x=3, y=1)
        self._update_quantity_in_cell(cell1, self.product, 10)
        tray_z = self._create_tray_z(self.tray_type_small_32x)
        cell2 = self._cell_for(tray_z, x=7, y=3)
        move = StockMove.create(
            {
                "name": "test_in_1",
                "location_id": cell1.id,
                "location_dest_id": cell2.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 2.0,
            }
        )
        StockMoveLine.create(
            {
                "move_id": move.id,
                "product_id": move.product_id.id,
                "qty_done": 1,
                "product_uom_id": move.product_uom.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
            }
        )
        self.move = move

    def test_compute_tray_matrix(self):
        self.create_stock_move()
        move_line = self.move.move_line_ids[0]
        move_line._compute_tray_matrix()
        self.assertEqual(
            move_line.tray_source_matrix,
            {
                "selected": [2, 0],
                # fmt: off
                'cells': [
                    [0, 0, 1, 0],
                    [0, 0, 0, 0],
                ]
                # fmt: on
            },
        )
        self.assertEqual(
            move_line.tray_dest_matrix,
            {
                "selected": [6, 2],
                # fmt: off
                'cells': [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
                # fmt: on
            },
        )

    def test_action_show_tray(self):
        self.create_stock_move()
        move_line = self.move.move_line_ids[0]
        view = move_line.action_show_source_tray()
        self.assertEqual(view["name"], "Source Tray")
        self.assertEqual(view["res_id"], move_line.id)
        view = move_line.action_show_dest_tray()
        self.assertEqual(view["res_id"], move_line.id)
