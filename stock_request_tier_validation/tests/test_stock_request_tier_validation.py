# Copyright 2017-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestStockRequest(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # common models
        cls.stock_request = cls.env["stock.request"]
        cls.request_order = cls.env["stock.request.order"]
        cls.tier_definition = cls.env["tier.definition"]

    def test_get_under_validation_exceptions(self):
        self.assertIn("route_id", self.stock_request._get_under_validation_exceptions())
        self.assertIn("route_id", self.request_order._get_under_validation_exceptions())

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "stock.request", self.tier_definition._get_tier_validation_model_names()
        )
        self.assertIn(
            "stock.request.order",
            self.tier_definition._get_tier_validation_model_names(),
        )
