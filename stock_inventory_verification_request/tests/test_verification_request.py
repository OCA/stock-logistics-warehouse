# Copyright 2020 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import AccessError


class TestStockVerificationRequest(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(
            no_reset_password=True)

        cls.obj_wh = cls.env['stock.warehouse']
        cls.obj_location = cls.env['stock.location']
        cls.obj_inventory = cls.env['stock.inventory']
        cls.obj_product = cls.env['product.product']
        cls.obj_svr = cls.env['stock.slot.verification.request']
        cls.obj_move = cls.env['stock.move']

        cls.product1 = cls.obj_product.create({
            'name': 'Test Product 1',
            'type': 'product',
            'default_code': 'PROD1',
        })
        cls.product2 = cls.obj_product.create({
            'name': 'Test Product 2',
            'type': 'product',
            'default_code': 'PROD2',
        })
        cls.test_loc = cls.obj_location.create({
            'name': 'Test Location',
            'usage': 'internal',
            'discrepancy_threshold': 0.1
        })

        # Create Stock manager able to force validation on inventories.
        group_stock_man = cls.env.ref('stock.group_stock_manager')
        group_inventory_all = cls.env.ref(
            'stock_inventory_discrepancy.'
            'group_stock_inventory_validation_always')
        cls.manager = cls.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'manager',
            'email': 'test.manager@example.com',
            'groups_id': [(6, 0, [group_stock_man.id, group_inventory_all.id])]
        })
        group_stock_user = cls.env.ref('stock.group_stock_user')
        cls.user = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'user',
            'email': 'test.user@example.com',
            'groups_id': [(6, 0, [group_stock_user.id])]
        })

        cls.starting_inv = cls.obj_inventory.create({
            'name': 'Starting inventory',
            'filter': 'product',
            'line_ids': [
                (0, 0, {
                    'product_id': cls.product1.id,
                    'product_uom_id': cls.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 2.0,
                    'location_id': cls.test_loc.id,
                }),
                (0, 0, {
                    'product_id': cls.product2.id,
                    'product_uom_id': cls.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 4.0,
                    'location_id': cls.test_loc.id,
                }),
            ],
        })
        cls.starting_inv.action_force_done()

    def test_svr_creation(self):
        """Tests the creation of Slot Verification Requests."""
        inventory = self.obj_inventory.create({
            'name': 'Generate over discrepancy in both lines.',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 3.0,
                    'location_id': self.test_loc.id,
                }),
                (0, 0, {
                    'product_id': self.product2.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 3.0,
                    'location_id': self.test_loc.id,
                })
            ],
        })
        inventory.with_context({'normal_view': True}).action_validate()
        self.assertEqual(inventory.state, 'pending',
                         'Inventory Adjustment not changing to Pending to '
                         'Approve.')
        previous_count = len(self.obj_svr.search([]))
        inventory.sudo(self.user).action_request_verification()
        current_count = len(self.obj_svr.search([]))
        self.assertEqual(current_count, previous_count + 2,
                         'Slot Verification Request not created.')
        # Test the method to open SVR from inventory lines:
        inventory.line_ids[0].action_open_svr()

    def test_svr_workflow(self):
        """Tests workflow of Slot Verification Request."""
        test_svr = self.env['stock.slot.verification.request'].create({
            'location_id': self.test_loc.id,
            'state': 'wait',
            'product_id': self.product1.id,
        })
        self.assertEqual(test_svr.state, 'wait',
                         'Slot Verification Request not created from scratch.')
        with self.assertRaises(AccessError):
            test_svr.sudo(self.user).action_confirm()
        test_svr.sudo(self.manager).action_confirm()
        self.assertEqual(test_svr.state, 'open',
                         'Slot Verification Request not confirmed properly.')
        test_svr.sudo(self.manager).action_solved()
        self.assertEqual(test_svr.state, 'done',
                         'Slot Verification Request not marked as solved.')
        test_svr.sudo(self.manager).action_cancel()
        self.assertEqual(test_svr.state, 'cancelled',
                         'Slot Verification Request not marked as cancelled.')

    def test_view_methods(self):
        """Tests the methods used to handle de UI."""
        test_svr = self.env['stock.slot.verification.request'].create({
            'location_id': self.test_loc.id,
            'state': 'wait',
            'product_id': self.product1.id,
        })
        test_svr.sudo(self.manager).action_confirm()
        self.assertEqual(test_svr.involved_move_count, 1,
                         'Unexpected involved move')
        self.assertEqual(test_svr.involved_inv_line_count, 1,
                         'Unexpected involved inventory line')
        test_svr.action_view_inv_lines()
        test_svr.action_view_moves()
