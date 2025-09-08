# Copyright 2017-2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProcurementAutoCreateGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.group_obj = cls.env["procurement.group"]
        cls.rule_obj = cls.env["stock.rule"]
        cls.route_obj = cls.env["stock.route"]
        cls.move_obj = cls.env["stock.move"]
        cls.picking_obj = cls.env["stock.picking"]
        cls.product_obj = cls.env["product.product"]

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.company_id = cls.env.ref("base.main_company")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.loc_components = cls.env.ref("stock.stock_location_components")
        picking_type_id = cls.env.ref("stock.picking_type_internal").id

        cls.partner = cls.env["res.partner"].create({"name": "Partner"})

        pull_push_route_auto = cls.route_obj.create({"name": "Auto Create Group"})
        cls.pull_push_rule_auto = cls.rule_obj.create(
            {
                "name": "rule with autocreate",
                "route_id": pull_push_route_auto.id,
                "auto_create_group": True,
                "action": "pull_push",
                "warehouse_id": cls.warehouse.id,
                "picking_type_id": picking_type_id,
                "location_dest_id": cls.location.id,
                "location_src_id": cls.loc_components.id,
                "partner_address_id": cls.partner.id,
            }
        )
        pull_push_route_no_auto = cls.route_obj.create(
            {"name": "Not Auto Create Group"}
        )
        cls.rule_obj.create(
            {
                "name": "rule with no autocreate",
                "route_id": pull_push_route_no_auto.id,
                "auto_create_group": False,
                "action": "pull_push",
                "warehouse_id": cls.warehouse.id,
                "picking_type_id": picking_type_id,
                "location_dest_id": cls.location.id,
                "location_src_id": cls.loc_components.id,
            }
        )
        push_route_auto = cls.route_obj.create({"name": "Auto Create Group Push"})
        cls.push_rule_auto = cls.rule_obj.create(
            {
                "name": "route_auto",
                "location_src_id": cls.location.id,
                "location_dest_id": cls.loc_components.id,
                "route_id": push_route_auto.id,
                "auto_create_group": True,
                "auto": "manual",
                "picking_type_id": picking_type_id,
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.company_id.id,
                "action": "push",
            }
        )
        push_route_no_auto = cls.route_obj.create(
            {"name": "Not Auto Create Group Push"}
        )
        cls.rule_obj.create(
            {
                "name": "route_no_auto",
                "location_src_id": cls.location.id,
                "location_dest_id": cls.loc_components.id,
                "route_id": push_route_no_auto.id,
                "auto_create_group": False,
                "auto": "manual",
                "picking_type_id": picking_type_id,
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.company_id.id,
                "action": "push",
            }
        )

        cls.prod_auto_pull_push_1 = cls.product_obj.create(
            {
                "name": "Test Product 1A - Same Route",
                "type": "product",
                "route_ids": [(6, 0, [pull_push_route_auto.id])],
            }
        )
        cls.prod_auto_pull_push_2 = cls.product_obj.create(
            {
                "name": "Test Product 1B - Same Route",
                "type": "product",
                "route_ids": [(6, 0, [pull_push_route_auto.id])],
            }
        )
        cls.prod_no_auto_pull_push = cls.product_obj.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "route_ids": [(6, 0, [pull_push_route_no_auto.id])],
            }
        )
        cls.prod_auto_push_1 = cls.product_obj.create(
            {
                "name": "Test Product 3A - Push Same Route",
                "type": "product",
                "route_ids": [(6, 0, [push_route_auto.id])],
            }
        )
        cls.prod_auto_push_2 = cls.product_obj.create(
            {
                "name": "Test Product 3B - Push Same Route",
                "type": "product",
                "route_ids": [(6, 0, [push_route_auto.id])],
            }
        )
        cls.prod_no_auto_push = cls.product_obj.create(
            {
                "name": "Test Product 4",
                "type": "product",
                "route_ids": [(6, 0, [push_route_no_auto.id])],
            }
        )

        cls.group = cls.group_obj.create({"name": "SO0001"})

    @classmethod
    def _procure(cls, product):
        values = {
            "group_id": cls.group,
            "route_ids": product.route_ids,
        }
        cls.group_obj.run(
            [
                cls.env["procurement.group"].Procurement(
                    product,
                    5.0,
                    product.uom_id,
                    cls.location,
                    "TEST",
                    "odoo tests",
                    cls.env.company,
                    values,
                )
            ]
        )

    @classmethod
    def _push_trigger(cls, product):
        picking = cls.picking_obj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": product.id,
                            "date_deadline": "2099-06-01 18:00:00",
                            "date": "2099-06-01 18:00:00",
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.move_ids.write({"quantity_done": 1.0})
        picking.button_validate()

    def test_01_pull_push_no_auto_create_group(self):
        """Test no auto creation of group - should use provided group."""
        move = self.move_obj.search(
            [("product_id", "=", self.prod_no_auto_pull_push.id)]
        )
        self.assertFalse(move)
        self._procure(self.prod_no_auto_pull_push)
        move = self.move_obj.search(
            [("product_id", "=", self.prod_no_auto_pull_push.id)]
        )
        self.assertTrue(move)
        self.assertEqual(
            move.group_id,
            self.group,
            "Should use the provided procurement group.",
        )

    def test_02_pull_push_auto_create_group(self):
        move = self.move_obj.search(
            [("product_id", "=", self.prod_auto_pull_push_1.id)]
        )
        self.assertFalse(move)
        self._procure(self.prod_auto_pull_push_1)
        move = self.move_obj.search(
            [("product_id", "=", self.prod_auto_pull_push_1.id)]
        )
        self.assertTrue(move)
        self.assertTrue(move.group_id, "Procurement Group not assigned.")

    def test_03_onchange_method(self):
        """Test onchange method for stock rule."""
        proc_rule = self.push_rule_auto
        self.assertTrue(proc_rule.auto_create_group)
        proc_rule.write({"group_propagation_option": "none"})
        proc_rule._onchange_group_propagation_option()
        self.assertFalse(proc_rule.auto_create_group)

    def test_04_push_no_auto_create_group(self):
        """Test push rule without auto_create_group."""
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_no_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertFalse(move)
        self._push_trigger(self.prod_no_auto_push)
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_no_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertTrue(move)
        self.assertFalse(
            move.group_id, "Procurement Group should not have been created."
        )

    def test_05_push_auto_create_group(self):
        """Test push rule with auto_create_group creates groups."""
        self._push_trigger(self.prod_auto_push_1)
        self._push_trigger(self.prod_auto_push_2)

        move_1 = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto_push_1.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        move_2 = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto_push_2.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )

        self.assertTrue(move_1)
        self.assertTrue(move_2)
        self.assertTrue(move_1.group_id, "Should create group for push product 1")
        self.assertTrue(move_2.group_id, "Should create group for push product 2")

        # Currently push rules create separate groups (original OCA behavior)
        self.assertNotEqual(
            move_1.group_id,
            move_2.group_id,
            "Push rules currently create separate groups",
        )

    def test_06_orderpoint_scheduler_route_grouping(self):
        """Test route grouping through orderpoint scheduler"""

        self.env["stock.quant"].search(
            [
                (
                    "product_id",
                    "in",
                    [self.prod_auto_pull_push_1.id, self.prod_auto_pull_push_2.id],
                )
            ]
        ).unlink()

        # Needing replenishment orderpoints
        orderpoint_1 = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.prod_auto_pull_push_1.id,
                "location_id": self.location.id,
                "product_min_qty": 10.0,
                "product_max_qty": 20.0,
                "route_id": self.prod_auto_pull_push_1.route_ids[0].id,
            }
        )
        orderpoint_2 = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.prod_auto_pull_push_2.id,
                "location_id": self.location.id,
                "product_min_qty": 10.0,
                "product_max_qty": 20.0,
                "route_id": self.prod_auto_pull_push_2.route_ids[0].id,
            }
        )

        orderpoint_1._compute_qty_to_order()
        orderpoint_2._compute_qty_to_order()

        self.assertGreater(
            orderpoint_1.qty_to_order, 0, "Orderpoint 1 should need replenishment"
        )
        self.assertGreater(
            orderpoint_2.qty_to_order, 0, "Orderpoint 2 should need replenishment"
        )

        (orderpoint_1 + orderpoint_2)._procure_orderpoint_confirm()

        move_1 = self.move_obj.search(
            [("product_id", "=", self.prod_auto_pull_push_1.id)]
        )
        move_2 = self.move_obj.search(
            [("product_id", "=", self.prod_auto_pull_push_2.id)]
        )

        self.assertTrue(move_1, "Move 1 should be created")
        self.assertTrue(move_2, "Move 2 should be created")

        self.assertTrue(move_1.group_id, "Move 1 should have group")
        self.assertTrue(move_2.group_id, "Move 2 should have group")
        self.assertEqual(
            move_1.group_id, move_2.group_id, "Should share same group via scheduler"
        )

    def test_07_orderpoint_no_auto_create_routes(self):
        """Test orderpoint scheduler when no routes have auto_create_group"""

        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.prod_no_auto_pull_push.id,
                "location_id": self.location.id,
                "product_min_qty": 10.0,
                "product_max_qty": 20.0,
                "route_id": self.prod_no_auto_pull_push.route_ids[0].id,
            }
        )

        self.env["stock.quant"].search(
            [("product_id", "=", self.prod_no_auto_pull_push.id)]
        ).unlink()
        orderpoint._compute_qty_to_order()
        self.assertGreater(orderpoint.qty_to_order, 0)

        orderpoint._procure_orderpoint_confirm()

        move = self.move_obj.search(
            [("product_id", "=", self.prod_no_auto_pull_push.id)]
        )
        self.assertTrue(move)
