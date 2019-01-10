# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestStockRequest(common.TransactionCase):
    def setUp(self):
        super(TestStockRequest, self).setUp()

        # common models
        self.stock_request = self.env['stock.request']
        self.request_order = self.env['stock.request.order']
        self.tier_definition = self.env['tier.definition']

    def test_get_under_validation_exceptions(self):
        self.assertIn('route_id',
                      self.stock_request._get_under_validation_exceptions())
        self.assertIn('route_id',
                      self.request_order._get_under_validation_exceptions())

    def test_get_tier_validation_model_names(self):
        self.assertIn('stock.request',
                      self.tier_definition._get_tier_validation_model_names())
        self.assertIn('stock.request.order',
                      self.tier_definition._get_tier_validation_model_names())
