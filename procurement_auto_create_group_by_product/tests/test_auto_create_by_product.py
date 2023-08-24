# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.procurement_auto_create_group.tests.test_auto_create import (
    TestProcurementAutoCreateGroup,
)


class TestProcurementAutoCreateGroupByProduct(TestProcurementAutoCreateGroup):
    def test_pull_push_auto_create_group_not_by_product(self):
        """Test pull flow that without option to group by product"""
        self.pull_push_rule_auto.auto_create_group_by_product = False
        # Behavior should be the same
        super(
            TestProcurementAutoCreateGroupByProduct, self
        ).test_02_pull_push_auto_create_group()

    def test_pull_push_auto_create_group_by_product(self):
        """Test pull flow that with option to group by product"""
        self.pull_push_rule_auto.auto_create_group_by_product = True
        move = self.move_obj.search([("product_id", "=", self.prod_auto_pull_push.id)])
        self.assertFalse(move)
        group = self.group_obj.search(
            [("product_id", "=", self.prod_auto_pull_push.id)]
        )
        self.assertFalse(move)
        self._procure(self.prod_auto_pull_push)
        move = self.move_obj.search([("product_id", "=", self.prod_auto_pull_push.id)])
        self.assertTrue(move)
        self.assertTrue(move.group_id, "Procurement Group not assigned.")
        self.assertEqual(
            move.group_id.product_id,
            self.prod_auto_pull_push,
            "Procurement Group product missing.",
        )
        self.assertEqual(
            move.product_uom_qty,
            5.0,
            "Move invalid quantity.",
        )
        self._procure(self.prod_auto_pull_push)
        group = self.group_obj.search(
            [("product_id", "=", self.prod_auto_pull_push.id)]
        )
        self.assertEqual(
            len(group),
            1,
            "Procurement Group per product should be unique.",
        )
        # The second move should be merged with the previous one
        self.assertEqual(
            move.product_uom_qty,
            10.0,
            "Move invalid quantity.",
        )

    def test_push_auto_create_group_not_by_product(self):
        """Test push flow that without option to group by product"""
        self.push_rule_auto.auto_create_group_by_product = False
        super(
            TestProcurementAutoCreateGroupByProduct, self
        ).test_05_push_auto_create_group()

    def test_push_auto_create_group_by_product(self):
        """Test push flow that with option to group by product"""
        self.push_rule_auto.auto_create_group_by_product = True
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
        self.assertEqual(
            move.group_id.product_id,
            self.prod_auto_push,
            "Procurement Group product missing.",
        )
        self._push_trigger(self.prod_auto_push)
        group = self.group_obj.search([("product_id", "=", self.prod_auto_push.id)])
        self.assertEqual(
            len(group),
            1,
            "Procurement Group per product should be unique.",
        )
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertEqual(
            len(move),
            1,
            "Invalid amount of moves.",
        )
        self.assertEqual(
            move.group_id.product_id,
            self.prod_auto_push,
            "Procurement Group product missing.",
        )
