from odoo.exceptions import AccessError, UserError
from odoo.tests.common import users

from odoo.addons.stock_multi_warehouse_security.tests.common import (
    TestStockCommon,
    allowed_companies,
)


class TestStockWarehouseAccess(TestStockCommon):
    @users("stock_user_c12_wh2")
    def test_read_stock_picking_limited_user(self):
        self.assertEqual(
            self.env["stock.picking"].search(
                [("warehouse_id", "in", self.warehouses.ids)]
            ),
            (self.stock_picking_wh_2),
        )

    @users("stock_user_c1_wh12")
    def test_read_stock_picking_unlimited_user(self):
        self.assertEqual(
            self.env["stock.picking"].search(
                [("warehouse_id", "in", self.warehouses.ids)]
            ),
            (self.stock_picking_wh_1 | self.stock_picking_wh_2),
        )

    @users("stock_user_c12_wh23")
    def test_read_stock_picking_multi_company(self):
        self.assertEqual(
            self.env["stock.picking"].search(
                [("warehouse_id", "in", self.warehouses.ids)]
            ),
            (self.stock_picking_wh_2 | self.stock_picking_wh_3),
        )

    @users("stock_user_c12_wh2")
    def test_read_stock_picking_type_limited_user(self):
        self.assertEqual(
            self.env["stock.picking.type"]
            .search([("warehouse_id", "in", self.warehouses.ids)])
            .mapped("warehouse_id"),
            (self.warehouse_2),
        )

    @users("stock_user_c1_wh12")
    def test_read_stock_picking_type_unlimited_user(self):
        self.assertEqual(
            self.env["stock.picking.type"]
            .search([("warehouse_id", "in", self.warehouses.ids)])
            .mapped("warehouse_id"),
            (self.warehouse_1 | self.warehouse_2),
        )

    @users("stock_user_c12_wh23")
    def test_read_stock_picking_type_multi_company(self):
        self.assertEqual(
            self.env["stock.picking.type"]
            .search([("warehouse_id", "in", self.warehouses.ids)])
            .mapped("warehouse_id"),
            (self.warehouse_2 | self.warehouse_3),
        )

    @users("stock_user_c12_wh2")
    def test_stock_user_wont_be_granted_by_ir_rule_to_create_stock_picking_type(self):
        with self.assertRaisesRegex(
            UserError,
            r"You are not allowed to create 'Picking Type' \(stock.picking.type\) records.*",
        ):
            self.env["stock.picking.type"].create(
                {
                    "name": "Test internal",
                    "sequence_code": "TEST-INT",
                    "code": "internal",
                    "warehouse_id": self.warehouse_2.id,
                }
            )

    @users(
        "stock_user_c12_wh2",
        "stock_user_c12_wh23",
        "stock_user_c1_wh12",
    )
    def test_create_and_validate_picking(self):
        picking = self._create_picking(
            self.warehouse_2, location_src=self.suppliers_location
        )
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        picking.move_ids.write({"quantity_done": 5})
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    @users(
        "stock_user_c12_wh2",
        "stock_user_c12_wh23",
    )
    def test_forbid_create_picking_other_warehouse(self):
        with self.assertRaisesRegex(
            AccessError, ".*Stock pickings from allowed Warehouse.*"
        ):
            self._create_picking(
                self.warehouse_1,
                location_src=self.suppliers_location,
                env=self.env,
            )

    @users(
        "stock_user_c1_wh12",
    )
    @allowed_companies()
    def test_read_stock_move_wh12(self):
        self.assertEqual(
            self.env["stock.move"]
            .search([("warehouse_id", "!=", self.warehouse_0.id)])
            .mapped("warehouse_id"),
            (self.warehouse_1 | self.warehouse_2),
        )

    @users(
        "stock_user_c12_wh2",
    )
    def test_read_stock_move_wh2_only(self):
        self.assertEqual(
            self.env["stock.move"].search([]).mapped("warehouse_id"), (self.warehouse_2)
        )

    @users(
        "stock_user_c12_wh23",
    )
    def test_read_stock_move_wh23(self):
        self.assertEqual(
            self.env["stock.move"].search([]).mapped("warehouse_id"),
            (self.warehouse_2 | self.warehouse_3),
        )

    @users(
        "stock_user_c12_wh2",
    )
    def test_read_stock_location_wh2_only(self):
        self.assertEqual(
            self.env["stock.location"].search([]).mapped("warehouse_id"),
            (self.warehouse_2),
        )

    @users(
        "stock_user_c12_wh23",
    )
    def test_read_stock_location_wh23(self):
        self.assertEqual(
            self.env["stock.location"].search([]).mapped("warehouse_id"),
            (self.warehouse_2 | self.warehouse_3),
        )

    @users(
        "stock_user_c1_wh12",
    )
    @allowed_companies()
    def test_read_stock_location_wh12(self):
        self.assertEqual(
            self.env["stock.location"]
            .search([("warehouse_id", "!=", self.warehouse_0.id)])
            .mapped("warehouse_id"),
            (self.warehouse_1 | self.warehouse_2),
        )

    @users(
        "stock_user_c12_wh2",
    )
    def test_read_stock_warehouse_orderpoint_wh2_only(self):
        self.assertEqual(
            self.env["stock.warehouse.orderpoint"].search([]).mapped("warehouse_id"),
            (self.warehouse_2),
        )

    @users(
        "stock_user_c12_wh23",
    )
    def test_read_stock_warehouse_orderpoint_wh23(self):
        self.assertEqual(
            self.env["stock.warehouse.orderpoint"].search([]).mapped("warehouse_id"),
            (self.warehouse_2 | self.warehouse_3),
        )

    @users(
        "stock_user_c1_wh12",
    )
    @allowed_companies()
    def test_read_stock_warehouse_orderpoint_wh12(self):
        self.assertEqual(
            self.env["stock.warehouse.orderpoint"]
            .search([("warehouse_id", "!=", self.warehouse_0.id)])
            .mapped("warehouse_id"),
            (self.warehouse_1 | self.warehouse_2),
        )


class TestStockWarehouseAccessWithReceivedGoods(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        pickings = (
            cls.stock_picking_wh_1 | cls.stock_picking_wh_2 | cls.stock_picking_wh_3
        )
        pickings.action_assign()
        pickings.move_ids.write({"quantity_done": 5})
        pickings.button_validate()

    @users(
        "stock_user_c12_wh2",
    )
    def test_read_stock_move_line_wh2_only(self):
        self.assertEqual(
            self.env["stock.move.line"].search([]).mapped("warehouse_id"),
            (self.warehouse_2),
        )

    @users(
        "stock_user_c12_wh23",
    )
    def test_read_stock_move_line_wh23(self):
        self.assertEqual(
            self.env["stock.move.line"].search([]).mapped("warehouse_id"),
            (self.warehouse_2 | self.warehouse_3),
        )

    @users(
        "stock_user_c1_wh12",
    )
    @allowed_companies()
    def test_read_stock_move_line_wh12(self):
        self.assertEqual(
            self.env["stock.move.line"]
            .search([("warehouse_id", "!=", self.warehouse_0.id)])
            .mapped("warehouse_id"),
            (self.warehouse_1 | self.warehouse_2),
        )

    @users(
        "stock_user_c12_wh2",
    )
    def test_read_stock_quant_wh2_only(self):
        self.assertEqual(
            self.env["stock.quant"].search([]).mapped("warehouse_id"),
            (self.warehouse_2),
        )

    @users(
        "stock_user_c12_wh23",
    )
    def test_read_stock_quant_wh23(self):
        self.assertEqual(
            self.env["stock.quant"].search([]).mapped("warehouse_id"),
            (self.warehouse_2 | self.warehouse_3),
        )

    @users(
        "stock_user_c1_wh12",
    )
    @allowed_companies()
    def test_read_stock_quant_wh12(self):
        self.assertEqual(
            self.env["stock.quant"]
            .search([("warehouse_id", "!=", self.warehouse_0.id)])
            .mapped("warehouse_id"),
            (self.warehouse_1 | self.warehouse_2),
        )


class TestStockWarehouseAccessWithReceivedPackedGoods(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        pickings = (
            cls.stock_picking_wh_1 | cls.stock_picking_wh_2 | cls.stock_picking_wh_3
        )
        pickings.action_assign()
        for picking in pickings:
            picking.move_line_ids.write(
                {
                    "result_package_id": cls.env["stock.quant.package"]
                    .create({"name": f"Dest Pack {picking.warehouse_id.name}"})
                    .id,
                    "qty_done": 5,
                }
            )
        pickings.button_validate()

    @users(
        "stock_user_c12_wh2",
    )
    def test_read_stock_quant_wh2_only(self):
        self.assertEqual(
            self.env["stock.quant.package"].search([]).mapped("warehouse_id"),
            (self.warehouse_2),
        )

    @users(
        "stock_user_c12_wh23",
    )
    def test_read_stock_quant_package_wh23(self):
        self.assertEqual(
            self.env["stock.quant.package"].search([]).mapped("warehouse_id"),
            (self.warehouse_2 | self.warehouse_3),
        )

    @users(
        "stock_user_c1_wh12",
    )
    @allowed_companies()
    def test_read_stock_quant_package_wh12(self):
        self.assertEqual(
            self.env["stock.quant.package"]
            .search([("warehouse_id", "!=", self.warehouse_0.id)])
            .mapped("warehouse_id"),
            (self.warehouse_1 | self.warehouse_2),
        )
