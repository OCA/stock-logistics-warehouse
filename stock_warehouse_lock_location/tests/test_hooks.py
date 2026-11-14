# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo.tests.common import TransactionCase

from .. import post_init_hook


class TestWarehouseLocationsHook(TransactionCase):
    """Warehouses get their lock location, on creation or on install."""

    def test_create_missing_locations_creates_lock_location(self):
        """A warehouse without a lock location gets one from the missing locations.

        Expected: an internal "Lock" location under the warehouse view location.
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.wh_lock_stock_loc_id = False

        warehouse._create_missing_locations({})
        warehouse = self.env["stock.warehouse"].browse(warehouse.id)

        self.assertTrue(warehouse.wh_lock_stock_loc_id)
        self.assertEqual(warehouse.wh_lock_stock_loc_id.name, "Lock")
        self.assertEqual(warehouse.wh_lock_stock_loc_id.usage, "internal")
        self.assertEqual(
            warehouse.wh_lock_stock_loc_id.location_id, warehouse.view_location_id
        )

    def test_post_init_hook_backfills_missing_lock_locations(self):
        """Installing the module gives existing warehouses a lock location."""
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.wh_lock_stock_loc_id = False

        post_init_hook(self.env)
        warehouse = self.env["stock.warehouse"].browse(warehouse.id)

        self.assertTrue(warehouse.wh_lock_stock_loc_id)
