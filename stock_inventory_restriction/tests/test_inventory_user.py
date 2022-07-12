# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestStockInventoryUser(TransactionCase):
    def setUp(self):
        super(TestStockInventoryUser, self).setUp()
        self.inventory_model = self.env["stock.inventory"]
        self.res_users_model = self.env["res.users"]

        self.company = self.env.ref("base.main_company")
        self.grp_stock_manager = self.env.ref("stock.group_stock_manager")
        self.grp_stock_user = self.env.ref("stock.group_stock_user")
        self.location = self.env.ref("stock.warehouse0").lot_stock_id

        self.manager = self.res_users_model.create(
            {
                "name": "Test Stock Manager",
                "login": "manager_1",
                "email": "example@yourcompany.com",
                "company_id": self.company.id,
                "company_ids": [(4, self.company.id)],
                "groups_id": [(6, 0, [self.grp_stock_manager.id])],
            }
        )
        self.user = self.res_users_model.create(
            {
                "name": "Test Stock User",
                "login": "user_1",
                "email": "example@yourcompany.com",
                "company_id": self.company.id,
                "company_ids": [(4, self.company.id)],
                "groups_id": [(6, 0, [self.grp_stock_user.id])],
            }
        )
        self.user_2 = self.res_users_model.create(
            {
                "name": "Test Stock User 2",
                "login": "user_2",
                "email": "example@yourcompany.com",
                "company_id": self.company.id,
                "company_ids": [(4, self.company.id)],
                "groups_id": [(6, 0, [self.grp_stock_user.id])],
            }
        )

    def test_inventory_user(self):
        inventory = self.inventory_model.with_user(self.manager).create({})
        self.assertTrue(inventory)
        inventory.write({"user_id": self.user})
        self.assertEqual(inventory.user_id, self.user)
        inventory.with_user(self.user).write(
            {"location_ids": [(6, 0, self.location.ids)]}
        )
        self.env["stock.inventory.line"].with_user(self.user).create(
            {
                "inventory_id": inventory.id,
                "product_id": self.env.ref("stock.product_cable_management_box").id,
                "location_id": self.location.id,
            }
        )
        self.assertEqual(inventory.location_ids, self.location)
        with self.assertRaises(AccessError):
            inventory.with_user(self.user_2).write({"location_ids": [(5, 0)]})
        with self.assertRaises(AccessError):
            self.env["stock.inventory.line"].with_user(self.user_2).create(
                {
                    "inventory_id": inventory.id,
                    "product_id": self.env.ref("stock.product_cable_management_box").id,
                    "location_id": self.location.id,
                }
            )
