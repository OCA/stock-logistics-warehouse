# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


# After every module is loaded: creating a warehouse needs the columns other
# installed modules add
@tagged("post_install", "-at_install")
class TestStockWarehouse(TransactionCase):
    """The stock types map to the warehouse locations, both ways."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Test Stock Type Warehouse", "code": "TSTW"}
        )

    def test_stock_type_location(self):
        """The free and quality types are the stock and quality locations."""
        self.assertEqual(
            self.warehouse._get_stock_type_location("free"),
            self.warehouse.lot_stock_id,
        )
        self.assertEqual(
            self.warehouse._get_stock_type_location("quality"),
            self.warehouse.wh_qc_stock_loc_id,
        )

    def test_unknown_stock_type(self):
        """An unknown stock type is refused."""
        with self.assertRaisesRegex(UserError, "^Unrecognized stock type: mystery$"):
            self.warehouse._get_stock_type_location("mystery")

    def test_required_stock_type_location(self):
        """A required stock type without location is refused, else it is empty."""
        self.warehouse.wh_qc_stock_loc_id = False
        self.assertFalse(self.warehouse._get_stock_type_location("quality"))
        with self.assertRaisesRegex(
            UserError,
            "^No Quality Control Location is set on warehouse "
            "Test Stock Type Warehouse$",
        ):
            self.warehouse._get_stock_type_location("quality", required=True)

    def test_location_stock_type(self):
        """A location gives its stock type, none for another location."""
        self.assertEqual(
            self.warehouse._get_location_stock_type(self.warehouse.lot_stock_id),
            "free",
        )
        self.assertEqual(
            self.warehouse._get_location_stock_type(self.warehouse.wh_qc_stock_loc_id),
            "quality",
        )
        self.assertIsNone(
            self.warehouse._get_location_stock_type(self.warehouse.view_location_id)
        )
