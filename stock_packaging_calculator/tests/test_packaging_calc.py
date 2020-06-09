# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestCalc(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
            }
        )
        cls.pkg_box = cls.env["product.packaging"].create(
            {"name": "Box", "product_id": cls.product_a.id, "qty": 50}
        )
        cls.pkg_big_box = cls.env["product.packaging"].create(
            {"name": "Big Box", "product_id": cls.product_a.id, "qty": 200}
        )
        cls.pkg_pallet = cls.env["product.packaging"].create(
            {"name": "Pallet", "product_id": cls.product_a.id, "qty": 2000}
        )

    def test_calc_1(self):
        """Test easy behavior 1."""
        expected = [
            {"id": self.pkg_pallet.id, "qty": 1, "name": self.pkg_pallet.name},
            {"id": self.pkg_big_box.id, "qty": 3, "name": self.pkg_big_box.name},
            {"id": self.pkg_box.id, "qty": 1, "name": self.pkg_box.name},
            {"id": self.uom_unit.id, "qty": 5, "name": self.uom_unit.name},
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(2655), expected)

    def test_calc_2(self):
        """Test easy behavior 2."""
        expected = [
            {"id": self.pkg_big_box.id, "qty": 1, "name": self.pkg_big_box.name},
            {"id": self.pkg_box.id, "qty": 3, "name": self.pkg_box.name},
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(350), expected)

    def test_calc_3(self):
        """Test easy behavior 3."""
        expected = [
            {"id": self.pkg_box.id, "qty": 1, "name": self.pkg_box.name},
            {"id": self.uom_unit.id, "qty": 30, "name": self.uom_unit.name},
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(80), expected)

    def test_calc_6(self):
        """Test fractional qty is lost."""
        expected = [
            {"id": self.pkg_box.id, "qty": 1, "name": self.pkg_box.name},
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(50.5), expected)

    def test_calc_sub1(self):
        """Test contained packaging behavior 1."""
        expected = [
            {
                "id": self.pkg_pallet.id,
                "qty": 1,
                "name": self.pkg_pallet.name,
                "contained": [
                    {
                        "id": self.pkg_big_box.id,
                        "qty": 10,
                        "name": self.pkg_big_box.name,
                    },
                ],
            },
            {
                "id": self.pkg_big_box.id,
                "qty": 3,
                "name": self.pkg_big_box.name,
                "contained": [
                    {"id": self.pkg_box.id, "qty": 4, "name": self.pkg_box.name},
                ],
            },
            {
                "id": self.pkg_box.id,
                "qty": 1,
                "name": self.pkg_box.name,
                "contained": [
                    {"id": self.uom_unit.id, "qty": 50, "name": self.uom_unit.name},
                ],
            },
            {
                "id": self.uom_unit.id,
                "qty": 5,
                "name": self.uom_unit.name,
                "contained": [],
            },
        ]
        self.assertEqual(
            self.product_a.product_qty_by_packaging(2655, with_contained=True),
            expected,
        )

    def test_calc_sub2(self):
        """Test contained packaging behavior 1."""
        self.pkg_box.qty = 30
        expected = [
            {
                "id": self.pkg_pallet.id,
                "qty": 1,
                "name": self.pkg_pallet.name,
                "contained": [
                    {
                        "id": self.pkg_big_box.id,
                        "qty": 10,
                        "name": self.pkg_big_box.name,
                    },
                ],
            },
            {
                "id": self.pkg_big_box.id,
                "qty": 3,
                "name": self.pkg_big_box.name,
                "contained": [
                    {"id": self.pkg_box.id, "qty": 6, "name": self.pkg_box.name},
                    {"id": self.uom_unit.id, "qty": 20, "name": self.uom_unit.name},
                ],
            },
            {
                "id": self.pkg_box.id,
                "qty": 1,
                "name": self.pkg_box.name,
                "contained": [
                    {"id": self.uom_unit.id, "qty": 30, "name": self.uom_unit.name},
                ],
            },
            {
                "id": self.uom_unit.id,
                "qty": 25,
                "name": self.uom_unit.name,
                "contained": [],
            },
        ]
        self.assertEqual(
            self.product_a.product_qty_by_packaging(2655, with_contained=True),
            expected,
        )
