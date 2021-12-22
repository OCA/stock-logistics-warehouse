from odoo.tests.common import SavepointCase


class TestUserRestriction(SavepointCase):
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
                "groups_id": [(6, 0, [cls.env.ref("stock.group_stock_user").id])],
            }
        )
        cls.stock_user_assigned_type = cls.env["res.users"].create(
            {
                "login": "stock_user_assigned_type",
                "name": "stock_user_assigned_type",
                "groups_id": [
                    (
                        6,
                        0,
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
            (6, 0, [self.stock_user_assigned_type.id])
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

        self.picking_type_out.assigned_user_ids = [(6, 0, [self.stock_user.id])]
        # assigned_user_ids is set with stock_user: only stock_user can read
        pick_types = self.picking_type_model.with_user(self.stock_user.id).search(
            [("name", "=", "Delivery Orders")]
        )
        self.assertTrue(self.picking_type_out in pick_types)
        pick_types = self.picking_type_model.with_user(
            self.stock_user_assigned_type.id
        ).search([("name", "=", "Delivery Orders")])
        self.assertFalse(self.picking_type_out in pick_types)
