# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast

from odoo.tests.common import SavepointCase


class TestStockOrderpointMoveLink(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_obj = cls.env["product.product"]
        cls.orderpoint_obj = cls.env["stock.warehouse.orderpoint"]
        cls.loc_obj = cls.env["stock.location"]
        cls.route_obj = cls.env["stock.location.route"]
        cls.group_obj = cls.env["procurement.group"]
        cls.move_obj = cls.env["stock.move"]
        cls.picking_obj = cls.env["stock.picking"]

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")

        # Create a new locations and routes:
        cls.intermediate_loc = cls.loc_obj.create(
            {
                "name": "Test location 1",
                "usage": "internal",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )
        cls.test_route = cls.route_obj.create(
            {
                "name": "Stock -> Test 1",
                "product_selectable": True,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "stock to test",
                            "action": "pull",
                            "location_id": cls.intermediate_loc.id,
                            "location_src_id": cls.stock_loc.id,
                            "procure_method": "make_to_stock",
                            "picking_type_id": cls.env.ref(
                                "stock.picking_type_internal"
                            ).id,
                        },
                    )
                ],
            }
        )
        cls.need_loc = cls.loc_obj.create(
            {
                "name": "Test location 2",
                "usage": "internal",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )
        cls.test_route_2 = cls.route_obj.create(
            {
                "name": "Test 1 -> Test 2",
                "product_selectable": True,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test 1 to Test 2",
                            "action": "pull",
                            "location_id": cls.need_loc.id,
                            "location_src_id": cls.intermediate_loc.id,
                            "procure_method": "make_to_order",
                            "picking_type_id": cls.env.ref(
                                "stock.picking_type_internal"
                            ).id,
                        },
                    )
                ],
            }
        )

        # Prepare Products:
        routes = cls.test_route_2 + cls.test_route
        cls.product = cls.product_obj.create(
            {"name": "Test Product", "route_ids": [(6, 0, routes.ids)]}
        )

        # Create Orderpoint:
        cls.orderpoint_need_loc = cls.orderpoint_obj.create(
            {
                "warehouse_id": cls.warehouse.id,
                "location_id": cls.need_loc.id,
                "product_id": cls.product.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "product_uom": cls.product.uom_id.id,
            }
        )
        cls.group_obj.run_scheduler()

    def test_01_stock_orderpoint_move_link(self):
        """Tests if manual procurement fills orderpoint_ids field."""
        move = self.move_obj.search(
            [("orderpoint_ids", "=", self.orderpoint_need_loc.id)]
        )
        self.assertTrue(len(move), 2)

    def test_02_stock_orderpoint_move_link_action_view(self):
        sp_orderpoint = self.move_obj.search(
            [("orderpoint_ids", "in", self.orderpoint_need_loc.id)]
        ).mapped("picking_id")
        result = self.orderpoint_need_loc.action_view_stock_picking()
        sp_action = self.picking_obj.search(ast.literal_eval(result["domain"]))
        self.assertEqual(sp_orderpoint, sp_action)
