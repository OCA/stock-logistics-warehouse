# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestStockInventoryUser(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.inventory_model = cls.env["stock.inventory"]
        cls.res_users_model = cls.env["res.users"]

        cls.company = cls.env.ref("base.main_company")
        cls.grp_stock_manager = cls.env.ref("stock.group_stock_manager")
        cls.grp_stock_user = cls.env.ref("stock.group_stock_user")
        cls.location = cls.env.ref("stock.warehouse0").lot_stock_id

        cls.manager = cls.res_users_model.create(
            {
                "name": "Test Stock Manager",
                "login": "manager_1",
                "email": "example@yourcompany.com",
                "company_id": cls.company.id,
                "company_ids": [Command.link(cls.company.id)],
                "groups_id": [Command.set(cls.grp_stock_manager.ids)],
            }
        )
        cls.user = cls.res_users_model.create(
            {
                "name": "Test Stock User",
                "login": "user_1",
                "email": "example@yourcompany.com",
                "company_id": cls.company.id,
                "company_ids": [Command.link(cls.company.id)],
                "groups_id": [Command.set(cls.grp_stock_user.ids)],
            }
        )
        cls.user_2 = cls.res_users_model.create(
            {
                "name": "Test Stock User 2",
                "login": "user_2",
                "email": "example@yourcompany.com",
                "company_id": cls.company.id,
                "company_ids": [Command.link(cls.company.id)],
                "groups_id": [Command.set(cls.grp_stock_user.ids)],
            }
        )

    def test_inventory_user(self):
        inventory = self.inventory_model.with_user(self.manager).create(
            {
                "responsible_id": self.user.id,
                "location_ids": [Command.set(self.location.ids)],
            }
        )
        # Assigned user can update its inventory
        inventory.with_user(self.user).write(
            {"location_ids": [Command.set(self.location.ids)]}
        )
        # Other users cannot
        with self.assertRaises(AccessError):
            inventory.with_user(self.user_2).write({"location_ids": [Command.clear()]})
        # Start inventory and check quants access
        inventory.action_state_to_in_progress()
        self.assertTrue(inventory.stock_quant_ids)
        quant = fields.first(inventory.stock_quant_ids)
        self.assertEqual(quant.user_id, self.user)
        # Users cannot modify inventoried quants of other users
        with self.assertRaises(AccessError):
            quant.with_user(self.user_2).action_set_inventory_quantity()
        # Working with the expected user
        quant.with_user(self.user).action_set_inventory_quantity()
        quant.action_clear_inventory_quantity()
        # Working with the stock manager too
        quant.with_user(self.manager).action_set_inventory_quantity()
