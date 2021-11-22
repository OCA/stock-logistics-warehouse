# Copyright 2017-2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProcurementAutoCreateGroup(TransactionCase):
    def setUp(self):
        super(TestProcurementAutoCreateGroup, self).setUp()
        self.group_obj = self.env["procurement.group"]
        self.rule_obj = self.env["stock.rule"]
        self.route_obj = self.env["stock.location.route"]
        self.move_obj = self.env["stock.move"]
        self.picking_obj = self.env["stock.picking"]
        self.product_obj = self.env["product.product"]

        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.env.ref("stock.stock_location_stock")
        self.company_id = self.env.ref("base.main_company")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.loc_components = self.env.ref("stock.stock_location_components")
        picking_type_id = self.env.ref("stock.picking_type_internal").id

        self.partner = self.env["res.partner"].create({"name": "Partner"})

        # Create rules and routes:
        pull_push_route_auto = self.route_obj.create({"name": "Auto Create Group"})
        self.rule_1 = self.rule_obj.create(
            {
                "name": "rule with autocreate",
                "route_id": pull_push_route_auto.id,
                "auto_create_group": True,
                "action": "pull_push",
                "warehouse_id": self.warehouse.id,
                "picking_type_id": picking_type_id,
                "location_id": self.location.id,
                "location_src_id": self.loc_components.id,
                "partner_address_id": self.partner.id,
            }
        )
        pull_push_route_no_auto = self.route_obj.create(
            {"name": "Not Auto Create Group"}
        )
        self.rule_obj.create(
            {
                "name": "rule with no autocreate",
                "route_id": pull_push_route_no_auto.id,
                "auto_create_group": False,
                "action": "pull_push",
                "warehouse_id": self.warehouse.id,
                "picking_type_id": picking_type_id,
                "location_id": self.location.id,
                "location_src_id": self.loc_components.id,
            }
        )
        push_route_auto = self.route_obj.create({"name": "Auto Create Group"})
        self.rule_1 = self.rule_obj.create(
            {
                "name": "route_auto",
                "location_src_id": self.location.id,
                "location_id": self.loc_components.id,
                "route_id": push_route_auto.id,
                "auto_create_group": True,
                "auto": "manual",
                "picking_type_id": picking_type_id,
                "warehouse_id": self.warehouse.id,
                "company_id": self.company_id.id,
                "action": "push",
            }
        )
        push_route_no_auto = self.route_obj.create({"name": "Not Auto Create Group"})
        self.rule_obj.create(
            {
                "name": "route_no_auto",
                "location_src_id": self.location.id,
                "location_id": self.loc_components.id,
                "route_id": push_route_no_auto.id,
                "auto_create_group": False,
                "auto": "manual",
                "picking_type_id": picking_type_id,
                "warehouse_id": self.warehouse.id,
                "company_id": self.company_id.id,
                "action": "push",
            }
        )

        # Prepare products:
        self.prod_auto_pull_push = self.product_obj.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "route_ids": [(6, 0, [pull_push_route_auto.id])],
            }
        )
        self.prod_no_auto_pull_push = self.product_obj.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "route_ids": [(6, 0, [pull_push_route_no_auto.id])],
            }
        )
        self.prod_auto_push = self.product_obj.create(
            {
                "name": "Test Product 3",
                "type": "product",
                "route_ids": [(6, 0, [push_route_auto.id])],
            }
        )
        self.prod_no_auto_push = self.product_obj.create(
            {
                "name": "Test Product 4",
                "type": "product",
                "route_ids": [(6, 0, [push_route_no_auto.id])],
            }
        )

    def _procure(self, product):
        values = {}
        self.group_obj.run(
            [
                self.env["procurement.group"].Procurement(
                    product,
                    5.0,
                    product.uom_id,
                    self.location,
                    "TEST",
                    "odoo tests",
                    self.env.company,
                    values,
                )
            ]
        )
        return True

    def _push_trigger(self, product):
        picking = self.picking_obj.create(
            {
                "picking_type_id": self.ref("stock.picking_type_in"),
                "location_id": self.supplier_location.id,
                "location_dest_id": self.location.id,
                "move_lines": [
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
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.location.id,
                        },
                    )
                ],
            }
        )
        picking.move_lines.write({"quantity_done": 1.0})
        picking.button_validate()

    def test_01_pull_push_no_auto_create_group(self):
        """Test auto creation of group."""
        move = self.move_obj.search(
            [("product_id", "=", self.prod_no_auto_pull_push.id)]
        )
        self.assertFalse(move)
        self._procure(self.prod_no_auto_pull_push)
        move = self.move_obj.search(
            [("product_id", "=", self.prod_no_auto_pull_push.id)]
        )
        self.assertTrue(move)
        self.assertFalse(
            move.group_id, "Procurement Group should not have been assigned."
        )

    def test_02_pull_push_auto_create_group(self):
        move = self.move_obj.search([("product_id", "=", self.prod_auto_pull_push.id)])
        self.assertFalse(move)
        self._procure(self.prod_auto_pull_push)
        move = self.move_obj.search([("product_id", "=", self.prod_auto_pull_push.id)])
        self.assertTrue(move)
        self.assertTrue(move.group_id, "Procurement Group not assigned.")
        self.assertEqual(
            move.group_id.partner_id,
            self.partner,
            "Procurement Group partner missing.",
        )

    def test_03_onchange_method(self):
        """Test onchange method for stock rule."""
        proc_rule = self.rule_1
        self.assertTrue(proc_rule.auto_create_group)
        proc_rule.write({"group_propagation_option": "none"})
        proc_rule._onchange_group_propagation_option()
        self.assertFalse(proc_rule.auto_create_group)

    def test_04_push_no_auto_create_group(self):
        """Test no auto creation of group."""
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
            move.group_id, "Procurement Group should not have been assigned."
        )

    def test_05_push_auto_create_group(self):
        """Test auto creation of group."""
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertFalse(move)
        self._push_trigger(self.prod_auto_push)
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertTrue(move)
        self.assertTrue(move.group_id, "Procurement Group not assigned.")
