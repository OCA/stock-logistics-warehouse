# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
from odoo.tests import common


class TestStockLockLot(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create(
            {"name": "Test category", "lot_default_locked": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "categ_id": cls.category.id}
        )

    def _get_lot_default_vals(self):
        return {
            "name": "Test lot",
            "product_id": self.product.id,
            "company_id": self.env.user.company_id.id,
        }

    def test_new_lot_unlocked(self):
        self.category.lot_default_locked = False
        lot = self.env["stock.production.lot"].create(self._get_lot_default_vals())
        self.assertFalse(lot.locked)

    def test_new_lot_locked(self):
        lot = self.env["stock.production.lot"].create(self._get_lot_default_vals())
        self.assertTrue(lot.locked)

    def test_lot_onchange_product(self):
        lot = self.env["stock.production.lot"].new(self._get_lot_default_vals())
        lot._onchange_product_id()
        self.assertTrue(lot.locked)

    def test_lock_permissions(self):
        self.env.user.groups_id -= self.env.ref("stock_lock_lot.group_lock_lot")
        # This should work correctly
        lot = self.env["stock.production.lot"].create(self._get_lot_default_vals())
        with self.assertRaises(exceptions.AccessError):
            lot.locked = False
