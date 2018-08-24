# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestInventoryDiscrepancy(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestInventoryDiscrepancy, self).setUp(*args, **kwargs)
        self.obj_wh = self.env['stock.warehouse']
        self.obj_location = self.env['stock.location']
        self.obj_inventory = self.env['stock.inventory']
        self.obj_product = self.env['product.product']
        self.obj_warehouse = self.env['stock.warehouse']
        self.obj_upd_qty_wizard = self.env['stock.change.product.qty']

        self.product1 = self.obj_product.create({
            'name': 'Test Product 1',
            'type': 'product',
            'default_code': 'PROD1',
        })
        self.product2 = self.obj_product.create({
            'name': 'Test Product 2',
            'type': 'product',
            'default_code': 'PROD2',
        })
        self.test_loc = self.obj_location.create({
            'name': 'Test Location',
            'usage': 'internal',
            'discrepancy_threshold': 0.1
        })
        self.test_wh = self.obj_warehouse.create({
            'name': 'Test WH',
            'code': 'T',
            'discrepancy_threshold': 0.2
        })
        self.obj_location._parent_store_compute()

        # Create Stock manager able to force validation on inventories.
        group_stock_man = self.env.ref('stock.group_stock_manager')
        group_inventory_all = self.env.ref(
            'stock_inventory_discrepancy.'
            'group_stock_inventory_validation_always')
        self.manager = self.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'manager',
            'email': 'test.manager@example.com',
            'groups_id': [(6, 0, [group_stock_man.id, group_inventory_all.id])]
        })
        group_stock_user = self.env.ref('stock.group_stock_user')
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'user',
            'email': 'test.user@example.com',
            'groups_id': [(6, 0, [group_stock_user.id])]
        })

        starting_inv = self.obj_inventory.create({
            'name': 'Starting inventory',
            'filter': 'product',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 2.0,
                    'location_id': self.test_loc.id,
                }),
                (0, 0, {
                    'product_id': self.product2.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 4.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        starting_inv.action_force_done()

    def test_compute_discrepancy(self):
        """Tests if the discrepancy is correctly computed.
        """
        inventory = self.obj_inventory.create({
            'name': 'Test Discrepancy Computation',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 3.0,
                    'location_id': self.test_loc.id,
                }),
                (0, 0, {
                    'product_id': self.product2.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 3.0,
                    'location_id': self.test_loc.id,
                })
            ],
        })
        self.assertEqual(inventory.line_ids[0].discrepancy_qty, 1.0,
                         'Wrong Discrepancy qty computation.')
        self.assertEqual(inventory.line_ids[1].discrepancy_qty, - 1.0,
                         'Wrong Discrepancy qty computation.')

    def test_discrepancy_validation(self):
        """Tests the new workflow"""
        inventory = self.obj_inventory.create({
            'name': 'Test Forcing Validation Method',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 3.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        self.assertEqual(inventory.state, 'draft',
                         'Testing Inventory wrongly configurated')
        self.assertEqual(inventory.line_ids.discrepancy_threshold, 0.1,
                         'Threshold wrongly computed in Inventory Line.')
        inventory.with_context({'normal_view': True}).action_done()
        self.assertEqual(inventory.over_discrepancy_line_count, 1,
                         'Computation of over-discrepancies failed.')
        self.assertEqual(inventory.state, 'pending',
                         'Inventory Adjustment not changing to Pending to '
                         'Approve.')
        inventory.sudo(self.manager).action_force_done()
        self.assertEqual(inventory.state, 'done',
                         'Forcing the validation of the inventory adjustment '
                         'not working properly.')

    def test_warehouse_threshold(self):
        """Tests the behaviour if the threshold is set on the WH."""
        inventory = self.obj_inventory.create({
            'name': 'Test Threshold Defined in WH',
            'location_id': self.test_wh.view_location_id.id,
            'filter': 'none',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 3.0,
                    'location_id': self.test_wh.lot_stock_id.id,
                }),
            ],
        })
        self.assertEqual(inventory.line_ids.discrepancy_threshold, 0.2,
                         'Threshold wrongly computed in Inventory Line.')

    def test_update_qty_user_error(self):
        """Test if a user error raises when a stock user tries to update the
        qty for a product and the correction is a discrepancy over the
        threshold."""
        upd_qty = self.obj_upd_qty_wizard.sudo(self.user).create({
            'product_id': self.product1.id,
            'product_tmpl_id': self.product1.product_tmpl_id.id,
            'new_quantity': 10.0,
            'location_id': self.test_loc.id,
        })
        with self.assertRaises(UserError):
            upd_qty.change_product_qty()
