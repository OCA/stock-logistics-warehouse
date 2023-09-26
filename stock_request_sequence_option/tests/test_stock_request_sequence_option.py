# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockRequestSequenceOption(TransactionCase):
    def setUp(self):
        super(TestStockRequestSequenceOption, self).setUp()
        self.StockRequest = self.env["stock.request"]
        self.StockRequestOrder = self.env["stock.request.order"]
        self.product_id = self.env.ref("product.product_product_6")
        self.expected_date = fields.Datetime.now()
        self.sr_vals = {
            "product_id": self.product_id.id,
            "product_uom_id": self.product_id.uom_id.id,
            "product_uom_qty": 5.0,
            "expected_date": self.expected_date,
        }
        self.sro_vals = {
            "expected_date": self.expected_date,
            "stock_request_ids": [(0, 0, self.sr_vals)],
        }
        self.sr_seq_opt = self.env.ref(
            "stock_request_sequence_option.stock_request_sequence_option"
        )
        self.sro_seq_opt = self.env.ref(
            "stock_request_sequence_option.stock_request_order_sequence_option"
        )

    def test_stock_request_sequence_options(self):
        """test with and without sequence option activated"""
        # With sequence option
        self.sr_seq_opt.use_sequence_option = True
        self.sr = self.StockRequest.create(self.sr_vals.copy())
        self.assertIn("SR-1", self.sr.name)
        # Without sequence option
        self.sr_seq_opt.use_sequence_option = False
        self.sr = self.StockRequest.create(self.sr_vals.copy())
        self.assertNotIn("SR-1", self.sr.name)

    def test_stock_request_order_sequence_options(self):
        """test with and without sequence option activated"""
        # With sequence option
        self.sro_seq_opt.use_sequence_option = True
        self.sro = self.StockRequestOrder.create(self.sro_vals.copy())
        self.assertIn("SRO-1", self.sro.name)
        # Without sequence option
        self.sro_seq_opt.use_sequence_option = False
        self.sro = self.StockRequestOrder.create(self.sro_vals.copy())
        self.assertNotIn("SRO-1", self.sro.name)
