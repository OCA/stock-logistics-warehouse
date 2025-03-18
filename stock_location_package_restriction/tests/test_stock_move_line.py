# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import ValidationError

from odoo.addons.stock_location_package_restriction.models.stock_location import (
    MULTIPACKAGE,
    NOPACKAGE,
    SINGLEPACKAGE,
)

from .common import ShortMoveInfo, TestLocationPackageRestrictionCommon


class TestMoveLine(TestLocationPackageRestrictionCommon):
    def test_move_line_multi_package(self):
        """
        Data:
            location_1 with pack1
            a move line with destination location_1
        Test case:
            Process the picking
        Expected result:
            The two packages are on location 2
        """
        self.location_2.package_restriction = MULTIPACKAGE
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_1,
        )
        self.location_1._check_package_restriction(move_lines=picking.move_line_ids)

    def test_move_line_no_package_success(self):
        """
        Data:
            location_1 with package restriction = 'no package'
            a move line with destination location_1
        Test case:
            Process the picking without result package
        Expected result:
            Picking processed
        """
        self.location_1.package_restriction = NOPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=False,
                ),
            ],
            location_dest=self.location_1,
        )
        self.location_1._check_package_restriction(move_lines=picking.move_line_ids)

    def test_move_line_no_package_error(self):
        """
        Data:
            location_1 with package restriction = 'no package'
            a move line with destination location_1
        Test case:
            Process the picking with result package
        Expected result:
            ValidationError
        """
        self.location_1.package_restriction = NOPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_1,
                ),
            ],
            location_dest=self.location_1,
        )
        with self.assertRaises(ValidationError):
            self.location_1._check_package_restriction(move_lines=picking.move_line_ids)

    def test_move_line_single_package_location_empty(self):
        """
        Data:
            location_1 without package but with package restriction = 'single package'
            a move line with two move with destination location_2
        Test case:
            Process the picking
        Expected result:
            ValidationError
        """
        self.location_1.package_restriction = SINGLEPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_1,
                ),
            ],
            location_dest=self.location_1,
        )
        self.location_1._check_package_restriction(move_lines=picking.move_line_ids)

    def test_move_line_single_package_location_not_empty(self):
        """
        Data:
            location_1 with product_1 but with package restriction = 'single package'
            a picking with one move: product_2 -> location_1
        Test case:
            Process the picking
        Expected result:
            ValidationError
        """
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.assertEqual(
            self.pack_1,
            self._get_package_in_location(self.location_1),
        )
        self.location_1.package_restriction = SINGLEPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_1,
        )
        with self.assertRaises(ValidationError):
            self.location_1._check_package_restriction(move_lines=picking.move_line_ids)
