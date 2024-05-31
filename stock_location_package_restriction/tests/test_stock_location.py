# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.stock_location_package_restriction.models.stock_location import (
    MULTIPACKAGE,
    NOPACKAGE,
    SINGLEPACKAGE,
)

from .common import TestLocationPackageRestrictionCommon


class TestStockLocation(TestLocationPackageRestrictionCommon):
    def test_location_no_package_location_ok(self):
        self._change_product_qty(self.product_1, self.location_1, False, 50)
        self.location_1.package_restriction = NOPACKAGE
        self.assertFalse(self.location_1.has_package_restriction_violation)

    def test_location_no_package_location_ko(self):
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.location_1.package_restriction = NOPACKAGE
        self.assertTrue(self.location_1.has_package_restriction_violation)

    def test_location_multi_package_location_ok(self):
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self._change_product_qty(self.product_1, self.location_1, self.pack_2, 50)
        self.location_1.package_restriction = MULTIPACKAGE
        self.assertFalse(self.location_1.has_package_restriction_violation)

    def test_location_multi_package_location_ko(self):
        self._change_product_qty(self.product_1, self.location_1, False, 50)
        self.location_1.package_restriction = MULTIPACKAGE
        self.assertTrue(self.location_1.has_package_restriction_violation)

    def test_location_single_package_location_ok(self):
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.location_1.package_restriction = SINGLEPACKAGE
        self.assertFalse(self.location_1.has_package_restriction_violation)

    def test_location_single_package_location_ko_multi(self):
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self._change_product_qty(self.product_1, self.location_1, self.pack_2, 50)
        self.location_1.package_restriction = SINGLEPACKAGE
        self.assertTrue(self.location_1.has_package_restriction_violation)

    def test_location_single_package_location_ko_no(self):
        self._change_product_qty(self.product_1, self.location_1, False, 50)
        self.location_1.package_restriction = SINGLEPACKAGE
        self.assertTrue(self.location_1.has_package_restriction_violation)
