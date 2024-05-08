# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form

from .test_common import TestCommon


class TestStockMoveLine(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.stock_picking_type.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.location_dest.id,
            }
        )

    def test_onchange_product_id_use_purchase_uom(self):
        self.stock_picking_type.use_purchase_uom = True
        stock_move_line = Form(self.env["stock.move.line"])
        stock_move_line.picking_id = self.picking
        stock_move_line.product_id = self.product
        self.assertEqual(stock_move_line.product_uom_id.id, self.product.uom_po_id.id)

    def test_onchange_product_id_no_use_purchase_uom(self):
        stock_move_line = Form(self.env["stock.move.line"])
        stock_move_line.picking_id = self.picking
        stock_move_line.product_id = self.product
        self.assertEqual(stock_move_line.product_uom_id.id, self.product.uom_id.id)
