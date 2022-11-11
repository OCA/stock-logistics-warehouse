# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockReceptionDedicatePickingType(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wh = cls.env.ref("stock.warehouse0")

    def test_1_two_steps_stock_in(self):
        self.assertFalse(self.wh.stock_in_type_id.active)
        self.wh.reception_steps = "two_steps"
        self.assertTrue(self.wh.stock_in_type_id.active)
        self.assertFalse(self.wh.quality_type_id.active)

    def test_2_three_steps_quality_check(self):
        self.assertFalse(self.wh.stock_in_type_id.active)
        self.assertFalse(self.wh.quality_type_id.active)
        self.wh.reception_steps = "three_steps"
        self.assertTrue(self.wh.stock_in_type_id.active)
        self.assertTrue(self.wh.quality_type_id.active)
