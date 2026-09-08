from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestUserRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                no_reset_password=True,
            )
        )
        cls.stock_user = cls.env["res.users"].create(
            {
                "login": "stock_user",
                "name": "stock_user",
                "group_ids": [Command.set([cls.env.ref("stock.group_stock_user").id])],
            }
        )
        cls.stock_user_assigned_type = cls.env["res.users"].create(
            {
                "login": "stock_user_assigned_type",
                "name": "stock_user_assigned_type",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref(
                                "stock_picking_type_user_restriction."
                                "group_assigned_picking_types_user"
                            ).id
                        ],
                    )
                ],
            }
        )
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_model = cls.env["stock.picking.type"]

    def test_access_picking_type(self):
        # Search delivery orders with standard stock users
        # It should be visible
        pick_types = self.picking_type_model.with_user(self.stock_user.id).search(
            [("name", "=", "Delivery Orders")]
        )
        self.assertTrue(self.picking_type_out in pick_types)
        # Search delivery orders with assigned stock users
        # It should not be visible
        pick_types = self.picking_type_model.with_user(
            self.stock_user_assigned_type.id
        ).search([("name", "=", "Delivery Orders")])
        self.assertFalse(self.picking_type_out in pick_types)

        # Assign delivery picking type to assigned user
        self.picking_type_out.assigned_user_ids = [
            Command.set([self.stock_user_assigned_type.id])
        ]
        # assigned_user_ids is set with stock_user_assigned_type: both users can read
        pick_types = self.picking_type_model.with_user(self.stock_user.id).search(
            [("name", "=", "Delivery Orders")]
        )
        self.assertTrue(self.picking_type_out in pick_types)
        pick_types = self.picking_type_model.with_user(
            self.stock_user_assigned_type.id
        ).search([("name", "=", "Delivery Orders")])
        self.assertTrue(self.picking_type_out in pick_types)

        self.picking_type_out.assigned_user_ids = [Command.set([self.stock_user.id])]
        # assigned_user_ids is set with stock_user: only stock_user can read
        pick_types = self.picking_type_model.with_user(self.stock_user.id).search(
            [("name", "=", "Delivery Orders")]
        )
        self.assertTrue(self.picking_type_out in pick_types)
        pick_types = self.picking_type_model.with_user(
            self.stock_user_assigned_type.id
        ).search([("name", "=", "Delivery Orders")])
        self.assertFalse(self.picking_type_out in pick_types)

    def test_assigned_user_is_internal_and_sees_inventory_menu(self):
        # The group must imply base.group_user, otherwise a user having only
        # this group is a portal-like user (share=True) that cannot read
        # ir.ui.menu and never sees the Inventory app
        user = self.stock_user_assigned_type
        self.assertFalse(user.share)
        self.assertTrue(user.has_group("base.group_user"))
        menu_ids = self.env["ir.ui.menu"].with_user(user)._visible_menu_ids()
        self.assertIn(self.env.ref("stock.menu_stock_root").id, menu_ids)
