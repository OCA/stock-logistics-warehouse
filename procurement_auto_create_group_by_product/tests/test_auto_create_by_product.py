# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import psycopg2

from odoo import api, registry, tools
from odoo.service.model import PG_CONCURRENCY_ERRORS_TO_RETRY

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

    def test_concurrent_procurement_group_creation(self):
        """Check for the same product, no multiple procurement groups are created."""
        rule = self.pull_push_rule_auto
        rule.auto_create_group_by_product = True
        product = self.prod_auto_pull_push
        # Check that no procurement group exist for the product
        self.assertFalse(product.auto_create_procurement_group_ids)
        # So create one and an adisory lock will be created
        rule._get_auto_procurement_group(product)
        self.assertTrue(product.auto_create_procurement_group_ids)
        # Use another transaction to test the advisory lock
        with registry(self.env.cr.dbname).cursor() as new_cr:
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)
            new_env["product.product"].invalidate_cache(
                ["auto_create_procurement_group_ids"],
                [
                    product.id,
                ],
            )
            rule2 = new_env["stock.rule"].browse(rule.id)
            rule2.auto_create_group_by_product = True
            product2 = new_env["product.product"].browse(product.id)
            self.assertFalse(product2.auto_create_procurement_group_ids)
            with self.assertRaises(psycopg2.OperationalError) as cm, tools.mute_logger(
                "odoo.sql_db"
            ):
                rule2._get_auto_procurement_group(product2)
            self.assertTrue(cm.exception.pgcode in PG_CONCURRENCY_ERRORS_TO_RETRY)
            new_cr.rollback()
