# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestWarehouseRelationship(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company_1 = cls.env.ref("base.main_company")

        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 1",
                "company_id": cls.company_1.id,
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WH1",
            }
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2",
                "company_id": cls.company_1.id,
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WH2",
            }
        )
        cls.warehouses = cls.warehouse_1 | cls.warehouse_2
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product for test",
                "type": "product",
            }
        )
        cls.stock_picking_wh_1 = cls._create_picking(
            cls.warehouse_1, location_src=cls.suppliers_location
        )
        cls.stock_picking_wh_2 = cls._create_picking(
            cls.warehouse_2, location_src=cls.suppliers_location
        )

    @classmethod
    def _create_picking(
        cls,
        warehouse,
        picking_type=None,
        location_src=None,
        location_dest=None,
        extra_stock_move_params=None,
        env=None,
    ):
        if not extra_stock_move_params:
            extra_stock_move_params = {}

        if not picking_type:
            picking_type = warehouse.in_type_id

        if not location_src:
            location_src = picking_type.default_location_src_id

        if not location_dest:
            location_dest = picking_type.default_location_dest_id

        if not env:
            env = cls.env

        location_src.ensure_one()
        location_dest.ensure_one()
        picking = (
            env["stock.picking"]
            .with_company(warehouse.company_id)
            .create(
                {
                    "picking_type_id": picking_type.id,
                    "location_id": location_src.id,
                    "location_dest_id": location_dest.id,
                }
            )
        )
        env["stock.move"].with_company(warehouse.company_id).create(
            dict(
                name="a move",
                product_id=cls.product.id,
                product_uom_qty=5.0,
                product_uom=cls.product.uom_id.id,
                picking_id=picking.id,
                location_id=location_src.id,
                location_dest_id=location_dest.id,
                **extra_stock_move_params,
            )
        )
        return picking

    def test_stock_picking_warehouse_id(self):
        self.assertEqual(self.stock_picking_wh_1.warehouse_id, self.warehouse_1)
        self.assertEqual(self.stock_picking_wh_2.warehouse_id, self.warehouse_2)

    def test_stock_move_warehouse_id(self):
        self.assertEqual(
            self.stock_picking_wh_1.move_lines.mapped("warehouse_id"), self.warehouse_1
        )
        self.assertEqual(
            self.stock_picking_wh_2.move_lines.mapped("warehouse_id"), self.warehouse_2
        )

    def test_stock_move_line_warehouse_id(self):
        (self.stock_picking_wh_1 | self.stock_picking_wh_2).action_assign()
        self.assertEqual(
            self.stock_picking_wh_1.move_line_ids.mapped("warehouse_id"),
            self.warehouse_1,
        )
        self.assertEqual(
            self.stock_picking_wh_2.move_line_ids.mapped("warehouse_id"),
            self.warehouse_2,
        )

    def test_stock_quant_warehouse_id(self):
        pickings = self.stock_picking_wh_1 | self.stock_picking_wh_2
        pickings.action_assign()
        pickings.move_lines.write({"quantity_done": 5})
        pickings.button_validate()

        self.assertEqual(
            self.env["stock.quant"].search_count(
                [("warehouse_id", "=", self.warehouse_1.id)]
            ),
            1,
        )
        self.assertEqual(
            self.env["stock.quant"].search_count(
                [("warehouse_id", "=", self.warehouse_2.id)]
            ),
            1,
        )

    def test_stock_quant_package_warehouse_id(self):
        pickings = self.stock_picking_wh_1 | self.stock_picking_wh_2
        pickings.action_assign()
        for picking in pickings:
            picking.move_line_ids.write(
                {
                    "result_package_id": self.env["stock.quant.package"]
                    .create({"name": f"Dest Pack {picking.warehouse_id.name}"})
                    .id,
                    "qty_done": 5,
                }
            )
        pickings.button_validate()

        self.assertEqual(
            self.env["stock.quant.package"].search_count(
                [("warehouse_id", "=", self.warehouse_1.id)]
            ),
            1,
        )
        self.assertEqual(
            self.env["stock.quant.package"].search_count(
                [("warehouse_id", "=", self.warehouse_2.id)]
            ),
            1,
        )

    def test_create_picking_with_picking_type(self):
        """improve coverage when picking_type_id is provide while
        creating stock move
        """
        picking_type = self.warehouse_2.in_type_id
        stock_picking = self._create_picking(
            self.warehouse_2,
            picking_type=picking_type,
            location_src=self.suppliers_location,
            extra_stock_move_params={"picking_type_id": picking_type.id},
        )
        stock_picking.action_assign()
        self.assertEqual(
            self.stock_picking_wh_2.move_lines.mapped("warehouse_id"), self.warehouse_2
        )
