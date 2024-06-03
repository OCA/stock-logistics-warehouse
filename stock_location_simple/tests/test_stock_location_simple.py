# Copyright 2018-2022 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestStockLocationSimple(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env["stock.warehouse"].search([])._check_locations_linked_to_warehouse()
        self.view_loc_id = self.env.ref("stock.warehouse0").view_location_id

    def test_native_location_checked(self):
        self.assertTrue(self.view_loc_id.is_linked_to_warehouse)

    def test_location_checked_at_warehouse_creation(self):
        new_wh_id = self.env["stock.warehouse"].create({"name": "Test", "code": "TEST"})
        self.assertTrue(new_wh_id.view_location_id.is_linked_to_warehouse)

    def test_change_location_linked_to_warehouse(self):
        new_loc_id = self.env["stock.location"].create({"name": "Test"})
        self.assertFalse(new_loc_id.is_linked_to_warehouse)

        self.env.ref("stock.warehouse0").write({"view_location_id": new_loc_id.id})
        self.assertTrue(new_loc_id.is_linked_to_warehouse)
        self.assertFalse(self.view_loc_id.is_linked_to_warehouse)
