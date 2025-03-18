# Copyright 2022-2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

from odoo import fields
from odoo.tests import tagged

from odoo.addons.stock_account.tests.test_stockvaluationlayer import (
    TestStockValuationStandard,
)


@tagged("post_install", "-at_install")
class TestStockValuationStandard(TestStockValuationStandard):
    def setUp(self):
        super(TestStockValuationStandard, self).setUp()

    @freeze_time("2022-12-02 23:00:00")
    def test_svl_accounting_date_real_time(self):
        self.product1.categ_id.property_valuation = "real_time"
        self.env.user.tz = "Asia/Tokyo"
        self._make_in_move(self.product1, 10)
        valuation_layer = self.product1.stock_valuation_layer_ids
        self.assertEqual(valuation_layer.accounting_date, date(2022, 12, 3))
        account_move = valuation_layer.account_move_id
        account_move.button_draft()
        account_move.name = "/"
        account_move.date = "2022-11-30"
        account_move.action_post()
        self.assertEqual(valuation_layer.accounting_date, date(2022, 11, 30))

    def test_svl_accounting_date_manual_periodic(self):
        # Not using freeze_time() in this test since it cannot be applied to create_date
        # without a hack.
        self.product1.categ_id.property_valuation = "manual_periodic"
        self._make_in_move(self.product1, 10)
        valuation_layer = self.product1.stock_valuation_layer_ids
        self.assertEqual(
            valuation_layer.accounting_date,
            fields.Date.context_today(valuation_layer, valuation_layer.create_date),
        )
