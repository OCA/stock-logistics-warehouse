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
        with Form(self.picking) as picking_form:
            with picking_form.move_ids_without_package.new() as move_line:
                move_line.product_id = self.product
                self.assertEqual(move_line.product_uom.id, self.product.uom_po_id.id)

    def test_onchange_product_id_no_use_purchase_uom(self):
        self.stock_picking_type.use_purchase_uom = False
        with Form(self.picking) as picking_form:
            with picking_form.move_ids_without_package.new() as move_line:
                move_line.product_id = self.product
                self.assertEqual(move_line.product_uom.id, self.product.uom_id.id)
