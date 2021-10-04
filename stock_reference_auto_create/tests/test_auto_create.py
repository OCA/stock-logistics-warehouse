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
        self.product_obj = self.env["product.product"]

        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.env.ref("stock.stock_location_stock")
        loc_components = self.env.ref("stock.stock_location_components")
        picking_type_id = self.env.ref("stock.picking_type_internal").id

        self.partner = self.env["res.partner"].create({"name": "Partner"})

        # Create rules and routes:
        route_auto = self.route_obj.create({"name": "Auto Create Group"})
        self.rule_1 = self.rule_obj.create(
            {
                "name": "rule with autocreate",
                "route_id": route_auto.id,
                "auto_create_group": True,
                "action": "pull_push",
                "warehouse_id": self.warehouse.id,
                "picking_type_id": picking_type_id,
                "location_id": self.location.id,
                "location_src_id": loc_components.id,
                "partner_address_id": self.partner.id,
            }
        )
        route_no_auto = self.route_obj.create({"name": "Not Auto Create Group"})
        self.rule_obj.create(
            {
                "name": "rule with no autocreate",
                "route_id": route_no_auto.id,
                "auto_create_group": False,
                "action": "pull_push",
                "warehouse_id": self.warehouse.id,
                "picking_type_id": picking_type_id,
                "location_id": self.location.id,
                "location_src_id": loc_components.id,
            }
        )

        # Prepare products:
        self.prod_auto = self.product_obj.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "route_ids": [(6, 0, [route_auto.id])],
            }
        )
        self.prod_no_auto = self.product_obj.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "route_ids": [(6, 0, [route_no_auto.id])],
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

    def test_01_no_auto_create_group(self):
        """Test auto creation of group."""
        move = self.move_obj.search([("product_id", "=", self.prod_no_auto.id)])
        self.assertFalse(move)
        self._procure(self.prod_no_auto)
        move = self.move_obj.search([("product_id", "=", self.prod_no_auto.id)])
        self.assertTrue(move)
        self.assertFalse(
            move.group_id, "Procurement Group should not have been assigned."
        )

    def test_02_auto_create_group(self):
        move = self.move_obj.search([("product_id", "=", self.prod_auto.id)])
        self.assertFalse(move)
        self._procure(self.prod_auto)
        move = self.move_obj.search([("product_id", "=", self.prod_auto.id)])
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
