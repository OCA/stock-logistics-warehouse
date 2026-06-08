# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests import tagged

from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


@tagged("-at_install", "post_install")
class TestStockRequestAnalyticTag(TestStockRequest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_tag_1 = cls.env["account.analytic.tag"].create(
            {"name": "Test Tag 1"}
        )
        cls.analytic_tag_2 = cls.env["account.analytic.tag"].create(
            {"name": "Test Tag 2"}
        )

    def test_stock_request_with_tag(self):
        """Stock request with single analytic tag."""
        request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 10,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "analytic_tag_ids": [(6, 0, [self.analytic_tag_1.id])],
            }
        )
        self.assertIn(self.analytic_tag_1, request.analytic_tag_ids)
        self.assertNotIn(self.analytic_tag_2, request.analytic_tag_ids)

    def test_stock_request_with_multiple_tags(self):
        """Stock request with multiple analytic tags."""
        request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 10,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "analytic_tag_ids": [
                    (6, 0, [self.analytic_tag_1.id, self.analytic_tag_2.id])
                ],
            }
        )
        self.assertIn(self.analytic_tag_1, request.analytic_tag_ids)
        self.assertIn(self.analytic_tag_2, request.analytic_tag_ids)

    def test_stock_request_without_tags(self):
        """Stock request without analytic tags."""
        request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 10,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
            }
        )
        self.assertFalse(request.analytic_tag_ids)
        self.assertNotIn(self.analytic_tag_1, request.analytic_tag_ids)
        self.assertNotIn(self.analytic_tag_2, request.analytic_tag_ids)
