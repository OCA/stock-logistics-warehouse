#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductHistory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu"}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.loss_location = cls.env["stock.location"].search(
            [
                ("company_id", "=", cls.env.company.id),
                ("scrap_location", "=", True),
            ],
            limit=1,
        )
        # Purchase moves
        purchase_move_vals_list = []
        for product_qty in [5, 5, 10]:
            purchase_move_vals_list.append(
                {
                    "product_id": cls.product.id,
                    "name": "Test In",
                    "product_uom_qty": product_qty,
                    "product_uom": cls.product.uom_id.id,
                    "location_id": cls.supplier_location.id,
                    "location_dest_id": cls.stock_location.id,
                    "state": "draft",
                }
            )
        cls.purchase_moves = cls.env["stock.move"].create(purchase_move_vals_list)
        cls.purchase_moves._action_confirm()
        cls.purchase_moves._action_assign()
        cls.purchase_moves.picked = True
        cls.purchase_moves._action_done()
        cls.purchase_moves.date = "2019-12-01"
        # Sales Moves
        sale_moves_vals_list = []
        for product_qty in [2, 5]:
            sale_moves_vals_list.append(
                {
                    "product_id": cls.product.id,
                    "name": "Test Out",
                    "product_uom_qty": product_qty,
                    "product_uom": cls.product.uom_id.id,
                    "location_id": cls.stock_location.id,
                    "location_dest_id": cls.customer_location.id,
                    "state": "draft",
                }
            )
        cls.sale_moves = cls.env["stock.move"].create(sale_moves_vals_list)
        cls.sale_moves._action_confirm()
        cls.sale_moves._action_assign()
        cls.sale_moves.picked = True
        cls.sale_moves._action_done()
        cls.sale_moves.date = "2019-12-21"
        # Loss Move
        cls.move_loss = cls.env["stock.move"].create(
            {
                "product_id": cls.product.id,
                "name": "Test Loss",
                "product_uom_qty": 3,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.loss_location.id,
            }
        )
        cls.move_loss._action_confirm()
        cls.move_loss._action_assign()
        cls.move_loss.picked = True
        cls.move_loss._action_done()
        cls.move_loss.date = "2020-01-01"

    def test_001_compute_weeks_history(self):
        self.product.history_range = "weeks"
        self.env["product.product"].job_compute_history("weeks", [self.product.id])
        self.assertEqual(
            self.product.product_history_ids[-1].end_qty,
            20.0,
            "End Quantity of a product should be 20.0",
        )
        self.assertEqual(
            self.product.product_history_ids[-1].purchase_qty,
            20.0,
            "Purchase Quantity of a product should be 13.0",
        )
        self.assertEqual(
            self.product.product_history_ids[-1].sale_qty,
            0.0,
            "Sale Quantity of a product should be 0.0",
        )
        self.assertEqual(
            self.product.product_history_ids[-4].sale_qty,
            -7.0,
            "Sale Quantity of a product should be -7.0",
        )
        self.assertEqual(
            self.product.product_history_ids[-6].loss_qty,
            -3.0,
            "Loss Quantity of a product should be -3.0",
        )
        self.assertEqual(
            self.product.product_history_ids[0].end_qty,
            10.0,
            "End Quantity of a product should be 10.0",
        )

    def test_002_compute_months_history(self):
        self.product.history_range = "months"
        self.env["product.product"].job_compute_history("months", [self.product.id])
        self.assertEqual(
            self.product.product_history_ids[-1].end_qty,
            13.0,
            "End Quantity of a product should be 13.0",
        )
        self.assertEqual(
            self.product.product_history_ids[-1].purchase_qty,
            20.0,
            "Purchase Quantity of a product should be 20.0",
        )
        self.assertEqual(
            self.product.product_history_ids[-1].sale_qty,
            -7.0,
            "Sale Quantity of a product should be -7.0",
        )
