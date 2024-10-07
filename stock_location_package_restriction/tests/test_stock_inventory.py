# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import ValidationError

from odoo.addons.stock_location_package_restriction.models.stock_location import (
    NOPACKAGE,
    SINGLEPACKAGE,
)

from .common import TestLocationPackageRestrictionCommon


class TestInventory(TestLocationPackageRestrictionCommon):
    def test_inventory_no_restriction(self):
        """
        Data:
            location_1 without package_restriction
            location_1 with 50 product_1 and pack_1
        Test case:
            Add qty of product_2 into location_1 with pack_2
        Expected result:
            The location contains the 2 products in 2 different packages
        """
        # Inventory Add product_1 to location_1
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.assertEqual(self.pack_1, self._get_package_in_location(self.location_1))

        self._change_product_qty(self.product_2, self.location_1, self.pack_2, 10)
        self.assertEqual(
            self.pack_1 | self.pack_2,
            self._get_package_in_location(self.location_1),
        )

    def test_inventory_no_package_success(self):
        """
        Data:
            location_1 with no package_restriction
        Test case:
            Add qty of product_1 into location_1
        Expected result:
            The location contains the product
        """
        self.location_1.package_restriction = NOPACKAGE
        # Inventory Add product_1 to location_1
        self._change_product_qty(self.product_1, self.location_1, False, 50)

    def test_inventory_no_package_error(self):
        """
        Data:
            location_1 with no package_restriction
        Test case:
            Add qty of product_1 into location_1 with pack_1
        Expected result:
            ValidationError
        """
        self.location_1.package_restriction = NOPACKAGE
        # Inventory Add product_1 to location_1
        with self.assertRaises(ValidationError):
            self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)

    def test_inventory_single_package(self):
        """
        Data:
            location_1 with single package restriction
            location_1 with 50 product_1 and pack_1
        Test case:
            Add qty of product_2 into location_1 with pack_2
        Expected result:
            ValidationError
        """
        # Inventory Add product_1 to location_1
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.assertEqual(self.pack_1, self._get_package_in_location(self.location_1))
        self.location_1.package_restriction = SINGLEPACKAGE
        with self.assertRaises(ValidationError):
            self._change_product_qty(self.product_2, self.location_1, self.pack_2, 10)
