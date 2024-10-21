# Copyright 2024 Ivan Perez <iperez@coninpe.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAssignInventoryResponsible(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "location_ids": [
                    (6, 0, [cls.env.ref("stock.stock_location_stock").id])
                ],
                "create_non_stocked": True,
                "product_selection": "all",
            }
        )
        cls.user_1 = cls.env["res.users"].create(
            {
                "name": "User 1",
                "login": "user1",
                "email": "",
                "signature": "",
                "groups_id": [(6, 0, [cls.env.ref("stock.group_stock_manager").id])],
            }
        )

    def test_assign_inventory_responsible_empty(self):
        self.stock_inventory._assign_responsible_of_inventory()
        self.assertEqual(self.stock_inventory.responsible_id, self.env.user)

    def test_assign_inventory_responsible(self):
        self.stock_inventory.responsible_id = self.user_1
        self.stock_inventory._assign_responsible_of_inventory()
        self.assertEqual(self.stock_inventory.responsible_id, self.user_1)
        self.assertNotEqual(self.stock_inventory.responsible_id, self.env.user)
