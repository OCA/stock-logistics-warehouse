# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestBarcode(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.in_type_id.display_picking_barcode = True

    def _create_picking(self):
        return (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=self.warehouse.in_type_id.id)
            .create({})
        )

    def test_barcode(self):
        picking = self._create_picking()
        self.assertTrue(picking.barcode)
        picking.name = "/"
        self.assertFalse(picking.barcode)
