# Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestProductAverageConsumption(TransactionCase):
    def setUp(self):
        super().setUp()
        Product = self.env["product.product"]

        # Create product template + product
        self.product = Product.create(
            {
                "name": "Test Product",
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        # Patch related fields on template
        tmpl = self.product.product_tmpl_id
        tmpl.consumption_calculation_method = "moves"
        tmpl.calculation_range = 365
        tmpl.display_range = 1

        # Stock locations
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.stock_location = self.env.ref("stock.stock_location_stock")

    def _create_stock_moves(self):
        StockMove = self.env["stock.move"]
        today = fields.Datetime.now()
        vals_list = []
        for i in range(5):
            vals_list.append(
                {
                    "name": f"Test Move {i}",
                    "product_id": self.product.id,
                    "product_uom_qty": 5,
                    "product_uom": self.product.uom_id.id,
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.customer_location.id,
                    "date": today - timedelta(days=i),
                    "state": "draft",
                }
            )
        moves = StockMove.create(vals_list)
        return moves

    def test_average_consumption_computation_values(self):
        """Ensure total_consumption, nb_days,
        and average_consumption are computed accurately."""
        moves = self._create_stock_moves()
        moves._action_done()
        self.product._compute_average_consumption()
        expected_total = 25.0
        self.assertAlmostEqual(
            self.product.total_consumption,
            expected_total,
            places=4,
            msg=f"""
                Expected total_consumption={expected_total},
                got {self.product.total_consumption}
            """,
        )
        first_move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id)], order="date asc", limit=1
        )
        expected_days = (fields.Datetime.now().date() - first_move.date.date()).days
        self.assertEqual(
            self.product.nb_days,
            expected_days,
            f"Expected nb_days={expected_days}, got {self.product.nb_days}",
        )
        expected_avg = expected_total / expected_days if expected_days else 0.0
        self.assertAlmostEqual(
            self.product.average_consumption,
            expected_avg,
            places=4,
            msg=f"""
                Expected average_consumption={expected_avg},
                got {self.product.average_consumption}
            """,
        )

    def test_displayed_average_consumption(self):
        """Ensure displayed_average_consumption multiplies
        correctly by display_range."""
        moves = self._create_stock_moves()
        moves._action_done()
        self.product._compute_average_consumption()
        self.product._compute_displayed_average_consumption()

        expected_displayed = (
            self.product.average_consumption * self.product.display_range
        )
        self.assertAlmostEqual(
            self.product.displayed_average_consumption,
            expected_displayed,
            places=4,
            msg="Displayed average consumption should match computed formula",
        )
