# Copyright 2024 Ivan Perez <iperez@coninpe.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestCheckInventoryResponsible(common.TransactionCase):
    def setUp(self):
        super(TestCheckInventoryResponsible, self).setUp()
        self.stock_inventory = self.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "location_ids": [
                    (6, 0, [self.env.ref("stock.stock_location_stock").id])
                ],
                "create_non_stocked": True,
                "product_selection": "all",
            }
        )
        self.user_1 = self.env["res.users"].create(
            {
                "name": "User 1",
                "login": "user1",
                "email": "",
                "signature": "",
                "groups_id": [(6, 0, [self.env.ref("stock.group_stock_manager").id])],
            }
        )

    def test_check_inventory_responsible_empty(self):
        self.stock_inventory._check_responsible_of_inventory()
        self.assertEqual(self.stock_inventory.responsible_id, self.env.user)

    def test_check_inventory_responsible(self):
        self.stock_inventory.responsible_id = self.user_1
        self.stock_inventory._check_responsible_of_inventory()
        self.assertEqual(self.stock_inventory.responsible_id, self.user_1)
        self.assertNotEqual(self.stock_inventory.responsible_id, self.env.user)
