# Copyright 2020 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from .common import TestCommon
from .utils import make_pkg_values


class TestCalc(TestCommon):
    def test_contained_mapping(self):
        self.assertEqual(
            self.product_a.packaging_contained_mapping,
            {
                str(self.pkg_pallet.id): [make_pkg_values(self.pkg_big_box, qty=10)],
                str(self.pkg_big_box.id): [make_pkg_values(self.pkg_box, qty=4)],
                str(self.pkg_box.id): [make_pkg_values(self.uom_unit, qty=50)],
            },
        )
        # Update pkg qty
        self.pkg_pallet.qty = 4000
        self.assertEqual(
            self.product_a.packaging_contained_mapping,
            {
                str(self.pkg_pallet.id): [make_pkg_values(self.pkg_big_box, qty=20)],
                str(self.pkg_big_box.id): [make_pkg_values(self.pkg_box, qty=4)],
                str(self.pkg_box.id): [make_pkg_values(self.uom_unit, qty=50)],
            },
        )

    def test_calc_1(self):
        """Test easy behavior 1."""
        expected = [
            make_pkg_values(self.pkg_pallet, qty=1),
            make_pkg_values(self.pkg_big_box, qty=3),
            make_pkg_values(self.pkg_box, qty=1),
            make_pkg_values(self.uom_unit, qty=5),
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(2655), expected)

    def test_calc_2(self):
        """Test easy behavior 2."""
        expected = [
            make_pkg_values(self.pkg_big_box, qty=1),
            make_pkg_values(self.pkg_box, qty=3),
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(350), expected)

    def test_calc_3(self):
        """Test easy behavior 3."""
        expected = [
            make_pkg_values(self.pkg_box, qty=1),
            make_pkg_values(self.uom_unit, qty=30),
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(80), expected)

    def test_calc_6(self):
        """Test fractional qty is lost."""
        expected = [
            make_pkg_values(self.pkg_box, qty=1),
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(50.5), expected)

    def test_calc_filter(self):
        """Test packaging filter."""
        expected = [
            make_pkg_values(self.pkg_big_box, qty=13),
            make_pkg_values(self.pkg_box, qty=1),
            make_pkg_values(self.uom_unit, qty=5),
        ]
        self.assertEqual(
            self.product_a.with_context(
                _packaging_filter=lambda x: x != self.pkg_pallet
            ).product_qty_by_packaging(2655),
            expected,
        )

    def test_calc_name_get(self):
        """Test custom name getter."""
        expected = [
            make_pkg_values(self.pkg_pallet, qty=1, name="FOO " + self.pkg_pallet.name),
            make_pkg_values(
                self.pkg_big_box, qty=3, name="FOO " + self.pkg_big_box.name
            ),
            make_pkg_values(self.pkg_box, qty=1, name="FOO " + self.pkg_box.name),
            make_pkg_values(self.uom_unit, qty=5, name=self.uom_unit.name),
        ]
        self.assertEqual(
            self.product_a.with_context(
                _packaging_name_getter=lambda x: "FOO " + x.name
            ).product_qty_by_packaging(2655),
            expected,
        )

    def test_calc_custom_values(self):
        """Test custom values handler."""
        expected = [
            {"my_qty": 1, "foo": self.pkg_pallet.name},
            {"my_qty": 3, "foo": self.pkg_big_box.name},
            {"my_qty": 1, "foo": self.pkg_box.name},
            {"my_qty": 5, "foo": self.uom_unit.name},
        ]
        self.assertEqual(
            self.product_a.with_context(
                _packaging_values_handler=lambda pkg, qty_per_pkg: {
                    "my_qty": qty_per_pkg,
                    "foo": pkg.name,
                }
            ).product_qty_by_packaging(2655),
            expected,
        )

    def test_calc_sub1(self):
        """Test contained packaging behavior 1."""
        expected = [
            make_pkg_values(
                self.pkg_pallet,
                qty=1,
                contained=[make_pkg_values(self.pkg_big_box, qty=10)],
            ),
            make_pkg_values(
                self.pkg_big_box,
                qty=3,
                contained=[make_pkg_values(self.pkg_box, qty=4)],
            ),
            make_pkg_values(
                self.pkg_box,
                qty=1,
                contained=[make_pkg_values(self.uom_unit, qty=50)],
            ),
            make_pkg_values(self.uom_unit, qty=5, contained=None),
        ]
        self.assertEqual(
            self.product_a.product_qty_by_packaging(2655, with_contained=True),
            expected,
        )

    def test_calc_sub2(self):
        """Test contained packaging behavior 2."""
        self.pkg_box.qty = 30
        expected = [
            make_pkg_values(
                self.pkg_pallet,
                qty=1,
                contained=[make_pkg_values(self.pkg_big_box, qty=10)],
            ),
            make_pkg_values(
                self.pkg_big_box,
                qty=3,
                contained=[
                    make_pkg_values(self.pkg_box, qty=6),
                    make_pkg_values(self.uom_unit, qty=20),
                ],
            ),
            make_pkg_values(
                self.pkg_box,
                qty=1,
                contained=[make_pkg_values(self.uom_unit, qty=30)],
            ),
            make_pkg_values(self.uom_unit, qty=25, contained=None),
        ]
        self.assertEqual(
            self.product_a.product_qty_by_packaging(2655, with_contained=True),
            expected,
        )
