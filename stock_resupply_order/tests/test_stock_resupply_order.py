from odoo.tests import tagged

from odoo.addons.stock_resupply_order.tests.common import StockResupplyOrderBaseCase


@tagged("post_install", "-at_install")
class TestStockResupplyOrderRun(StockResupplyOrderBaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.resupply_order = cls.env["stock.resupply.order"].create(
            {
                "location_id": cls.location.id,
            }
        )

        cls.env["stock.resupply.order.line"].create(
            {
                "stock_resupply_order_id": cls.resupply_order.id,
                "product_id": cls.env["product.product"]
                .search([("product_tmpl_id", "=", cls.product_template.id)], limit=1)
                .id,
                "quantity": 10,
            }
        )

        cls.lot = cls.env["stock.production.lot"].create(
            {
                "name": "lot disposable 1",
                "product_id": cls.product_disposable.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )

    def test_create_and_run_resupply_order(self):
        procurement = self.resupply_order.action_run()
        self.assertEqual(self.resupply_order.action_run(), procurement)

        self.resupply_order._compute_picking_ids()
        self.assertEqual(len(self.resupply_order.picking_ids), 1)
        self.assertEqual(self.resupply_order.picking_count, 1)
        self.assertEqual(
            self.resupply_order.picking_ids[0]
            .move_ids_without_package[0]
            .product_uom_qty,
            10,
        )

    def test_create_and_run_resupply_order_with_partial_stock(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product_disposable,
            self.env.ref("stock_resupply_order.location_dest_demo"),
            6,
            lot_id=self.lot,
        )

        self.resupply_order.action_run()
        self.resupply_order._compute_picking_ids()

        self.assertEqual(
            self.resupply_order.picking_ids[0]
            .move_ids_without_package[0]
            .product_uom_qty,
            4,
        )

    def test_create_and_run_resupply_order_with_complete_stock(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product_disposable,
            self.env.ref("stock_resupply_order.location_dest_demo"),
            10,
            lot_id=self.lot,
        )

        self.resupply_order.action_run()
        self.resupply_order._compute_picking_ids()

        self.assertEqual(len(self.resupply_order.picking_ids), 0)

    def test_create_and_run_empty_resupply_order(self):
        self.resupply_order = self.env["stock.resupply.order"].create(
            {
                "location_id": self.location.id,
            }
        )

        service_product_template = (
            self.env["product.template"]
            .sudo()
            .create(
                {
                    "name": "my service",
                    "type": "service",
                    "default_code": "default_code",
                }
            )
        )

        self.env["stock.resupply.order.line"].create(
            {
                "stock_resupply_order_id": self.resupply_order.id,
                "product_id": self.env["product.product"]
                .search(
                    [("product_tmpl_id", "=", service_product_template.id)], limit=1
                )
                .id,
                "quantity": 10,
            }
        )

        self.resupply_order.action_run()

        self.resupply_order._compute_picking_ids()
        self.assertEqual(len(self.resupply_order.picking_ids), 0)


@tagged("post_install", "-at_install")
class TestStockResupplyOrderView(StockResupplyOrderBaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.resupply_order = cls.env["stock.resupply.order"].create(
            {
                "location_id": cls.location.id,
            }
        )

    def test_view_transfer_without_pickings(self):
        self.resupply_order.action_run()
        result = self.resupply_order.action_view_transfers()

        self.assertEqual(result["name"], "Transfers")
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_view_transfer_with_single_picking(self):
        self.env["stock.resupply.order.line"].create(
            {
                "stock_resupply_order_id": self.resupply_order.id,
                "product_id": self.env["product.product"]
                .search([("product_tmpl_id", "=", self.product_template.id)], limit=1)
                .id,
                "quantity": 10,
            }
        )

        self.resupply_order.action_run()
        result = self.resupply_order.action_view_transfers()

        self.assertEqual(len(self.resupply_order.picking_ids), 1)
        self.assertEqual(result["res_id"], self.resupply_order.picking_ids.id)
        self.assertEqual(
            result["views"], [(self.env.ref("stock.view_picking_form").id, "form")]
        )

    def test_view_transfer_with_multiple_pickings(self):
        product = self.env["product.product"].search(
            [("product_tmpl_id", "=", self.product_template.id)], limit=1
        )
        self.env["stock.resupply.order.line"].create(
            {
                "stock_resupply_order_id": self.resupply_order.id,
                "product_id": product.id,
                "quantity": 10,
            }
        )

        self.resupply_order.action_run()

        # Create a second picking manually to force the view to show multiple pickings.
        self.env["stock.picking"].create(
            {
                "location_id": self.env.ref(
                    "stock_resupply_order.location_stock_demo"
                ).id,
                "location_dest_id": self.env.ref(
                    "stock_resupply_order.location_dest_demo"
                ).id,
                "picking_type_id": self.env.ref(
                    "stock_resupply_order.picking_type_demo"
                ).id,
                "immediate_transfer": False,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "DummyMoveLine",
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 1.0,
                            "group_id": self.resupply_order.procurement_group_id.id,
                        },
                    )
                ],
            }
        )

        result = self.resupply_order.action_view_transfers()

        self.assertEqual(
            result["domain"],
            [
                (
                    "id",
                    "in",
                    self.resupply_order.procurement_group_id.stock_move_ids.picking_id.ids,
                )
            ],
        )
