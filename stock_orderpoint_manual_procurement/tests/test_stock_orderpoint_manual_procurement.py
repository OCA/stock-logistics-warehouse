# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockWarehouseOrderpoint(common.TransactionCase):

    def setUp(self):
        super(TestStockWarehouseOrderpoint, self).setUp()

        # Refs
        self.group_stock_manager = self.env.ref('stock.group_stock_manager')
        self.group_change_procure_qty = self.env.ref(
            'stock_orderpoint_manual_procurement.'
            'group_change_orderpoint_procure_qty')
        self.company1 = self.env.ref('base.main_company')

        # Get required Model
        self.reordering_rule_model = self.env['stock.warehouse.orderpoint']
        self.product_model = self.env['product.product']
        self.user_model = self.env['res.users']
        self.product_ctg_model = self.env['product.category']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.make_procurement_orderpoint_model =\
            self.env['make.procurement.orderpoint']

        # Create users
        self.user = self._create_user('user_1',
                                      [self.group_stock_manager,
                                       self.group_change_procure_qty],
                                      self.company1)
        # Get required Model data
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.location = self.env.ref('stock.stock_location_stock')
        self.product = self.env.ref('product.product_product_7')

        # Create Product category and Product
        self.product_ctg = self._create_product_category()
        self.product = self._create_product()

        # Add default quantity
        quantity = 20.00
        self._update_product_qty(self.product, self.location, quantity)

        # Create Reordering Rule
        self.reorder = self.create_orderpoint()

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            self.user_model.with_context({'no_reset_password': True}).create({
                'name': 'Test User',
                'login': login,
                'password': 'demo',
                'email': 'test@yourcompany.com',
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, group_ids)]
            })
        return user

    def _create_product_category(self):
        """Create a Product Category."""
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'type': 'normal',
        })
        return product_ctg

    def _create_product(self):
        """Create a Product."""
        product = self.product_model.create({
            'name': 'Test Product',
            'categ_id': self.product_ctg.id,
            'type': 'product',
            'uom_id': self.product_uom.id,
        })
        return product

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        change_product_qty = self.stock_change_model.create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        change_product_qty.change_product_qty()
        return change_product_qty

    def create_orderpoint(self):
        """Create a Reordering Rule"""
        reorder = self.reordering_rule_model.sudo(self.user).create({
            'name': 'Order-point',
            'product_id': self.product.id,
            'product_min_qty': '100',
            'product_max_qty': '500',
            'qty_multiple': '1'
        })
        return reorder

    def create_orderpoint_procurement(self):
        """Make Procurement from Reordering Rule"""
        context = {
            'active_model': 'stock.warehouse.orderpoint',
            'active_ids': self.reorder.ids,
            'active_id': self.reorder.id
        }
        wizard = self.make_procurement_orderpoint_model.sudo(self.user).\
            with_context(context).create({})
        wizard.make_procurement()
        return wizard

    def test_security(self):
        """Test Manual Procurement created from Order-Point"""

        # Create Manual Procurement from order-point procured quantity
        self.create_orderpoint_procurement()

        # Assert that Procurement is created with the desired quantity
        self.assertTrue(self.reorder.procurement_ids)
        self.assertEqual(self.reorder.product_id.id,
                         self.reorder.procurement_ids.product_id.id)
        self.assertEqual(self.reorder.name,
                         self.reorder.procurement_ids.origin)
        self.assertNotEqual(self.reorder.procure_recommended_qty,
                            self.reorder.procurement_ids.product_qty)
        self.assertEqual(self.reorder.procurement_ids.product_qty,
                         480.0)
