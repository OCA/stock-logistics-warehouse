# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from .test_common import TestCommon


class TestStockMove(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_onchange_product_id(self):
        self.stock_move._onchange_product_id()
        self.assertEqual(self.stock_move.product_uom.id, self.product.uom_id.id)

        self.stock_picking_type.use_purchase_uom = True

        self.stock_move._onchange_product_id()
        self.assertEqual(self.stock_move.product_uom.id, self.product.uom_po_id.id)
