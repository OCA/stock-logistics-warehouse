# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo.tests.common import SavepointCase


class TestPackagingCalc(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPackagingCalc, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.uom_unit = cls.env.ref("product.product_uom_unit")
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
            }
        )
        cls.product_tmpl_a = cls.product_a.product_tmpl_id
        cls.pkg_box = cls.env["product.packaging"].create(
            {
                "name": "Box",
                "product_tmpl_id": cls.product_tmpl_a.id,
                "qty": 50,
            }
        )
        cls.pkg_big_box = cls.env["product.packaging"].create(
            {
                "name": "Big Box",
                "product_tmpl_id": cls.product_tmpl_a.id,
                "qty": 200,
            }
        )
        cls.pkg_pallet = cls.env["product.packaging"].create(
            {
                "name": "Pallet",
                "product_tmpl_id": cls.product_tmpl_a.id,
                "qty": 2000,
            }
        )

    @classmethod
    def _generate_expected_contained_mapping(cls, expected_result_map):
        """
        get the general structure for mapping. structure be like :
        str(self.pkg_pallet.id): [
                    {
                        "id": self.pkg_big_box.id,
                        "qty": 10,
                        "name": self.pkg_big_box.name,
                        "is_unit": False,
                    },
                ]
        """
        return {
            str(item[0]): [
                {
                    "id": item[1][0],
                    "qty": item[1][1],
                    "name": item[1][2],
                    "is_unit": item[1][3],
                }
            ]
            for item in expected_result_map
        }

    @classmethod
    def _generate_expected_packaging_info(
        cls, expected_info, extended_name=None
    ):
        return [
            {
                "id": package_info[0].id,
                "qty": package_info[1],
                "name": extended_name + package_info[0].name
                if extended_name and package_info[0].id != cls.uom_unit.id
                else package_info[0].name,
                "is_unit": package_info[2],
            }
            for package_info in expected_info
        ]

    def test_contained_mapping(self):
        pkg_pallet = (
            self.pkg_pallet.id,
            (self.pkg_big_box.id, 10, self.pkg_big_box.name, False),
        )
        pkg_big_box = (
            self.pkg_big_box.id,
            (self.pkg_box.id, 4, self.pkg_box.name, False),
        )
        pkg_box = (
            self.pkg_box.id,
            (self.uom_unit.id, 50, self.uom_unit.name, True),
        )
        expected_mapping = self._generate_expected_contained_mapping(
            [pkg_pallet, pkg_big_box, pkg_box]
        )
        self.assertEqual(
            self.product_a.packaging_contained_mapping, expected_mapping
        )
        # Update pkg qty
        self.pkg_pallet.qty = 4000
        pkg_pallet = (
            self.pkg_pallet.id,
            (self.pkg_big_box.id, 20, self.pkg_big_box.name, False),
        )
        expected_mapping = self._generate_expected_contained_mapping(
            [pkg_pallet, pkg_big_box, pkg_box]
        )
        self.assertEqual(
            self.product_a.packaging_contained_mapping, expected_mapping
        )

    def test_calc_1(self):
        """Test easy behavior 1."""
        pallet_info = (self.pkg_pallet, 1, False)
        big_box_info = (self.pkg_big_box, 3, False)
        box_info = (self.pkg_box, 1, False)
        unit_info = (self.uom_unit, 5, True)
        expected = self._generate_expected_packaging_info(
            [pallet_info, big_box_info, box_info, unit_info]
        )
        self.assertEqual(
            self.product_a.product_qty_by_packaging(2655), expected
        )

    def test_calc_2(self):
        """Test easy behavior 2."""
        big_box_info = (self.pkg_big_box, 1, False)
        box_info = (self.pkg_box, 3, False)
        expected = self._generate_expected_packaging_info(
            [big_box_info, box_info]
        )
        self.assertEqual(
            self.product_a.product_qty_by_packaging(350), expected
        )

    def test_calc_3(self):
        """Test easy behavior 3."""
        box_info = (self.pkg_box, 1, False)
        unit_info = (self.uom_unit, 30, True)
        expected = self._generate_expected_packaging_info(
            [box_info, unit_info]
        )
        self.assertEqual(self.product_a.product_qty_by_packaging(80), expected)

    def test_calc_4(self):
        """Test fractional qty is  in the unit package."""
        unit_info = (self.uom_unit, 1, True)
        box_info = (self.pkg_box, 1, False)
        expected = self._generate_expected_packaging_info(
            [box_info, unit_info]
        )
        self.assertEqual(
            self.product_a.product_qty_by_packaging(50.5), expected
        )

    def test_calc_filter(self):
        """Test packaging filter."""
        big_box_info = (self.pkg_big_box, 13, False)
        box_info = (self.pkg_box, 1, False)
        unit_info = (self.uom_unit, 5, True)
        expected = self._generate_expected_packaging_info(
            [big_box_info, box_info, unit_info]
        )
        with self.product_a.product_qty_by_packaging_arg_ctx(
            packaging_filter=lambda x: x != self.pkg_pallet
        ):
            self.assertEqual(
                self.product_a.product_qty_by_packaging(2655), expected,
            )

    def test_calc_name_get(self):
        """Test custom name getter."""

        pallet_info = (self.pkg_pallet, 1, False)
        big_box_info = (self.pkg_big_box, 3, False)
        box_info = (self.pkg_box, 1, False)
        unit_info = (self.uom_unit, 5, True)
        extended_name = "FOO "
        expected = self._generate_expected_packaging_info(
            [pallet_info, big_box_info, box_info, unit_info],
            extended_name=extended_name,
        )
        with self.product_a.product_qty_by_packaging_arg_ctx(
            packaging_name_getter=lambda x: "FOO " + x.name
        ):
            self.assertEqual(
                self.product_a.product_qty_by_packaging(2655), expected,
            )

    def test_calc_custom_values(self):
        """Test custom values handler."""
        expected = [
            {"my_qty": 1, "foo": self.pkg_pallet.name},
            {"my_qty": 3, "foo": self.pkg_big_box.name},
            {"my_qty": 1, "foo": self.pkg_box.name},
            {"my_qty": 5, "foo": self.uom_unit.name},
        ]
        with self.product_a.product_qty_by_packaging_arg_ctx(
            packaging_values_handler=lambda pkg, qty_per_pkg: {
                "my_qty": qty_per_pkg,
                "foo": pkg.name,
            }
        ):

            self.assertEqual(
                self.product_a.product_qty_by_packaging(2655), expected,
            )

    def test_calc_sub1(self):
        """Test contained packaging behavior 1."""
        expected = [
            {
                "id": self.pkg_pallet.id,
                "qty": 1,
                "name": self.pkg_pallet.name,
                "is_unit": False,
                "contained": [
                    {
                        "id": self.pkg_big_box.id,
                        "qty": 10,
                        "name": self.pkg_big_box.name,
                        "is_unit": False,
                    },
                ],
            },
            {
                "id": self.pkg_big_box.id,
                "qty": 3,
                "name": self.pkg_big_box.name,
                "is_unit": False,
                "contained": [
                    {
                        "id": self.pkg_box.id,
                        "qty": 4,
                        "name": self.pkg_box.name,
                        "is_unit": False,
                    },
                ],
            },
            {
                "id": self.pkg_box.id,
                "qty": 1,
                "name": self.pkg_box.name,
                "is_unit": False,
                "contained": [
                    {
                        "id": self.uom_unit.id,
                        "qty": 50,
                        "name": self.uom_unit.name,
                        "is_unit": True,
                    },
                ],
            },
            {
                "id": self.uom_unit.id,
                "qty": 5,
                "name": self.uom_unit.name,
                "is_unit": True,
                "contained": None,
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
                "is_unit": False,
                "contained": [
                    {
                        "id": self.pkg_big_box.id,
                        "qty": 10,
                        "name": self.pkg_big_box.name,
                        "is_unit": False,
                    },
                ],
            },
            {
                "id": self.pkg_big_box.id,
                "qty": 3,
                "name": self.pkg_big_box.name,
                "is_unit": False,
                "contained": [
                    {
                        "id": self.pkg_box.id,
                        "qty": 6,
                        "name": self.pkg_box.name,
                        "is_unit": False,
                    },
                    {
                        "id": self.uom_unit.id,
                        "qty": 20,
                        "name": self.uom_unit.name,
                        "is_unit": True,
                    },
                ],
            },
            {
                "id": self.pkg_box.id,
                "qty": 1,
                "name": self.pkg_box.name,
                "is_unit": False,
                "contained": [
                    {
                        "id": self.uom_unit.id,
                        "qty": 30,
                        "name": self.uom_unit.name,
                        "is_unit": True,
                    },
                ],
            },
            {
                "id": self.uom_unit.id,
                "qty": 25,
                "name": self.uom_unit.name,
                "is_unit": True,
                "contained": None,
            },
        ]
        self.assertEqual(
            self.product_a.product_qty_by_packaging(2655, with_contained=True),
            expected,
        )
