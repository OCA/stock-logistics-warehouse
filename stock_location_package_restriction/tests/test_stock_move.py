# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import ValidationError

from odoo.addons.stock_location_package_restriction.models.stock_location import (
    MULTIPACKAGE,
    NOPACKAGE,
    SINGLEPACKAGE,
)

from .common import ShortMoveInfo, TestLocationPackageRestrictionCommon


class TestStockMove(TestLocationPackageRestrictionCommon):
    def test_picking_multi_package(self):
        """
        Data:
            location_2 without product nor package restriction
            a picking with two move with destination location_2
        Test case:
            Process the picking
        Expected result:
            The two packages are on location 2
        """
        self.location_2.package_restriction = MULTIPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_2,
                    qty=2,
                    package_id=self.pack_1,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_2,
                    qty=4,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_2,
        )
        self._process_picking(picking)
        self.assertEqual(
            self.pack_1 | self.pack_2,
            self._get_package_in_location(self.location_2),
        )

    def test_picking_no_package_success(self):
        """
        Data:
            location_1 with package restriction = 'no package'
            a picking with destination location_1
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
        self._process_picking(picking)

    def test_picking_no_package_error(self):
        """
        Data:
            location_1 with package restriction = 'no package'
            a picking with destination location_1
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
            self._process_picking(picking)

    def test_picking_single_package_location_empty(self):
        """
        Data:
            location_2 without package but with package restriction = 'single package'
            a picking with two move with destination location_2
        Test case:
            Process the picking
        Expected result:
            ValidationError
        """
        self.location_2.package_restriction = SINGLEPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_2,
                    qty=2,
                    package_id=self.pack_1,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_2,
                    qty=2,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_2,
        )
        with self.assertRaises(ValidationError):
            self._process_picking(picking)

    def test_picking_single_package_with_backorder(self):
        """
        Data:
            location_2 without package but with package restriction = 'single package'
            a picking with two move with destination location_2 but only one move is
            being processsed, backorder creation.
        Test case:
            Process the picking
        Expected result:
            One package in location no error
        """
        self.location_2.package_restriction = SINGLEPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_2,
                    qty=2,
                    package_id=self.pack_1,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_2,
                    qty=2,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_2,
        )
        picking.action_assign()
        # Processing only one move out of two
        line_to_process = picking.move_line_ids[0]
        line_to_process.qty_done = line_to_process.product_qty
        wizard_action = picking.button_validate()
        wizard_context = wizard_action.get("context", {})
        wizard = (
            self.env[wizard_action["res_model"]]
            .with_context(**wizard_context)
            .create({})
        )
        wizard.process()
        self.assertEqual(self.pack_1, self._get_package_in_location(self.location_2))

    def test_picking_no_restriction(self):
        """
        Data:
            location_1 with product_1 and without package restriction = 'single package'
            a picking with two moves:
             * product_1 -> location_1,
             * product_2 -> location_1
        Test case:
            Process the picking
        Expected result:
            We now have two products into the same location
        """
        # Inventory Add product_1 to location_1
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.assertEqual(
            self.pack_1,
            self._get_package_in_location(self.location_1),
        )
        self.location_1.package_restriction = False
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_1,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_1,
        )
        self._process_picking(picking)
        self.assertEqual(
            self.pack_1 | self.pack_2,
            self._get_package_in_location(self.location_1),
        )

    def test_picking_single_package_location_not_empty(self):
        """
        Data:
            location_1 with product_1 but with package restriction = 'single package'
            a picking with one move: product_2 -> location_1
        Test case:
            Process the picking
        Expected result:
            ValidationError
        """
        # Inventory Add product_1 to location_1
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
            self._process_picking(picking)
