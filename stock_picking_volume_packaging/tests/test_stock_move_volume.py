# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockMoveVolume(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "product_length": 10.0,
                "product_width": 5.0,
                "product_height": 3.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.pkg_box = cls.env["product.packaging"].create(
            {
                "name": "Box",
                "product_id": cls.product.id,
                "qty": 5,
                "barcode": "BOX",
                "length_uom_id": cls.env.ref("uom.product_uom_meter").id,
            }
        )
        cls.pkg_big_box = cls.env["product.packaging"].create(
            {
                "name": "Big Box",
                "product_id": cls.product.id,
                "qty": 10,
                "barcode": "BIGBOX",
                "length_uom_id": cls.env.ref("uom.product_uom_meter").id,
            }
        )

    def test_move_volume_package_no_dimension(self):
        """
        Data:
            one product template with dimensions
            no dimensions on packaging
        Test Case:
            get the move volume for a quantity of 16
        Expected result:
            volume is 16 * 10 * 5 * 3 = 2400
        """
        move = self.env["stock.move"].new(
            {"product_id": self.product, "product_uom_qty": 16}
        )
        self.assertEqual(move.product_id._get_volume_for_qty(16), 2400)

    def test_move_volume_package_with_dimension(self):
        """
        Data:
            one product template with dimensions
            Volumes on packaging are:
             - box: 1
             - big box: 2
        Test Case:
            get the move volume for a quantity of 16
        Expected result:
            volume
              - unit: 1 * 10 * 5 * 3 = 150
              - box: 1 * 1 * 1 * 1 = 1
              - big box: 2 * 1 * 1 * 1 = 2
            volume total = 150 + 1 + 2 = 153
        """
        self.pkg_box.write(
            {
                "packaging_length": 1,
                "width": 1,
                "height": 1,
            }
        )
        self.pkg_big_box.write(
            {
                "packaging_length": 1,
                "width": 1,
                "height": 2,
            }
        )
        move = self.env["stock.move"].new(
            {"product_id": self.product, "product_uom_qty": 16}
        )

        self.assertEqual(move.product_id._get_volume_for_qty(16), 153)
