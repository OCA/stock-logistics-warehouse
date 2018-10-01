# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import exceptions
from datetime import datetime
from datetime import date, timedelta


class TestStockInventoryRevaluation(TransactionCase):
    """Test that the Inventory is Revaluated when the
    inventory price for any product is changed."""

    def setUp(self):
        super(TestStockInventoryRevaluation, self).setUp()
        # Get required Model
        self.product_model = self.env['product.product']
        self.template_model = self.env['product.template']
        self.product_ctg_model = self.env['product.category']
        self.reval_model = self.env['stock.inventory.revaluation']
        self.account_model = self.env['account.account']
        self.get_quant_model = self.\
            env['stock.inventory.revaluation.get.quant']
        self.mass_post_model = self.\
            env['stock.inventory.revaluation.mass.post']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.stock_location_model = self.env['stock.location']
        self.res_users_model = self.env['res.users']

        # Get required Model data
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.company = self.env.ref('base.main_company')

        # groups
        self.group_inventory_valuation = self.env.ref(
            'stock_account.group_inventory_valuation')
        self.group_stock_user = self.env.ref(
            'stock.group_stock_user')

        location = self.stock_location_model.search([('name', '=', 'WH')])
        self.location = self.stock_location_model.search([('location_id', '=',
                                                           location.id)])

        # Account types
        expense_type = self.env.ref('account.data_account_type_expenses')
        equity_type = self.env.ref('account.data_account_type_equity')
        asset_type = self.env.ref('account.data_account_type_fixed_assets')\

        # Create account for Goods Received Not Invoiced
        name = 'Goods Received Not Invoiced'
        code = 'grni'
        acc_type = equity_type
        self.account_grni = self._create_account(acc_type, name, code,
                                                 self.company)
        # Create account for Cost of Goods Sold
        name = 'Cost of Goods Sold'
        code = 'cogs'
        acc_type = expense_type
        self.account_cogs = self._create_account(acc_type, name, code,
                                                 self.company)

        # Create account for Inventory
        name = 'Inventory'
        code = 'inventory'
        acc_type = asset_type
        self.account_inventory = self._create_account(acc_type, name, code,
                                                      self.company)

        # Create account for Inventory Revaluation
        name = 'Inventory Revaluation'
        code = 'revaluation'
        acc_type = expense_type
        self.account_revaluation = self._create_account(acc_type, name, code,
                                                        self.company)

        # Create product category
        self.product_ctg = self._create_product_category()

        # Create users
        self.user1 = self._create_user('user_1',
                                       [self.group_stock_user,
                                        self.group_inventory_valuation],
                                       self.company)

        # Create a Product with real cost
        standard_price = 10.0
        list_price = 20.0
        self.product_real_1 = self._create_product('real', standard_price,
                                                   False, list_price)
        self.product_real_2 = self._create_product(
            False, False, self.product_real_1.product_tmpl_id, list_price)

        # Add default quantity
        quantity = 10.00
        self._update_product_qty(self.product_real_1, self.location, quantity)
        self._update_product_qty(self.product_real_2, self.location, quantity)

        # Create a Product with average cost
        standard_price = 10.0
        list_price = 20.0
        self.product_average_1 = self._create_product('average',
                                                      standard_price,
                                                      False,
                                                      list_price)
        self.product_average_2 = self._create_product(
            False, False, self.product_average_1.product_tmpl_id, list_price)

        # Add default quantity
        quantity = 10.00
        self._update_product_qty(self.product_average_1, self.location,
                                 quantity)
        self._update_product_qty(self.product_average_2, self.location,
                                 quantity)

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            self.res_users_model.with_context(
                {'no_reset_password': True}).create(
                {'name': 'Test User',
                 'login': login,
                 'password': 'demo',
                 'email': 'test@yourcompany.com',
                 'company_id': company.id,
                 'company_ids': [(4, company.id)],
                 'groups_id': [(6, 0, group_ids)]
                 })
        return user

    def _create_account(self, acc_type, name, code, company):
        """Create an account."""
        account = self.account_model.create({
            'name': name,
            'code': code,
            'user_type_id': acc_type.id,
            'company_id': company.id,
        })
        return account

    def _create_product_category(self):
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.account_inventory.id,
            'property_inventory_revaluation_increase_account_categ':
                self.account_revaluation.id,
            'property_inventory_revaluation_decrease_account_categ':
                self.account_revaluation.id,
            'property_valuation': 'real_time',
        })
        return product_ctg

    def _create_product(self, cost_method, standard_price, template,
                        list_price):
        """Create a Product variant."""
        if not template:
            template = self.template_model.create({
                'name': 'test_product',
                'categ_id': self.product_ctg.id,
                'type': 'product',
                'standard_price': standard_price,
                'valuation': 'real_time',
                'cost_method': cost_method,
                'property_stock_account_input': self.account_grni.id,
                'property_stock_account_output': self.account_cogs.id,
            })
            return template.product_variant_ids[0]
        product = self.product_model.create(
            {'product_tmpl_id': template.id,
             'list_price': list_price})
        return product

    def _create_inventory_revaluation(self, revaluation_type,
                                      product):
        """Create a Inventory Revaluation by applying
         increase and decrease account to it."""
        self.increase_account_id = product.categ_id and \
            product.categ_id.\
            property_inventory_revaluation_increase_account_categ
        self.decrease_account_id = product.categ_id and \
            product.categ_id.\
            property_inventory_revaluation_decrease_account_categ

        reval = self.reval_model.sudo(self.user1).create({
            'name': 'test_inventory_revaluation',
            'document_date': datetime.today(),
            'revaluation_type': revaluation_type,
            'product_id': product.id,
            'increase_account_id': self.increase_account_id.id,
            'decrease_account_id': self.decrease_account_id.id,
        })
        return reval

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        product_qty = self.stock_change_model.create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def _get_quant(self, date_from, revaluation):
        """Get Quants for Inventory Revaluation between the date supplied."""
        quant = self.get_quant_model.create({
            'date_from': date_from,
            'date_to': datetime.today(),
        })
        line_context = {
            'active_id': revaluation.id,
            'active_ids': revaluation.ids,
            'active_model': 'stock.inventory.revaluation',
        }
        quant.with_context(line_context).process()
        for reval_quant in revaluation.reval_quant_ids:
            reval_quant.new_cost = 8.0

    def _mass_post(self, revaluations):
        """Get Quants for Inventory Revaluation between the date supplied."""
        context = {
            'active_id': revaluations[0],
            'active_ids': [rev.id for rev in revaluations],
            'active_model': 'stock.inventory.revaluation',
        }
        mass_post_wiz = self.mass_post_model.sudo(self.user1).with_context(
            context).create({})
        mass_post_wiz.process()
        return True

    def test_defaults(self):
        """Test default methods"""
        self.assertNotEqual(self.reval_model._default_journal(), False)

    def test_inventory_revaluation_price_change_real(self):
        """Test that the inventory is revaluated when the
        inventory price for a product managed under real costing method is
        changed."""
        # Create an Inventory Revaluation for real cost product
        revaluation_type = 'price_change'
        invent_price_change_real = \
            self._create_inventory_revaluation(
                revaluation_type,
                self.product_real_1)

        # Create an Inventory Revaluation Line Quant
        date_from = date.today() - timedelta(1)
        self._get_quant(date_from, invent_price_change_real)

        invent_price_change_real.sudo(self.user1).button_post()

        expected_result = (10.00 - 8.00) * 10.00
        self.assertEqual(len(
            invent_price_change_real.account_move_ids[0].line_ids), 2,
            'Incorrect accounting entry generated')

        for move_line in invent_price_change_real.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(move_line.credit, expected_result,
                                 'Incorrect inventory revaluation for '
                                 'type Price Change.')

        quants = self.env['stock.quant'].search([('product_id', '=',
                                                 self.product_real_1.id)])

        # We should be able to delete the quants afterwards
        quants.with_context(force_unlink=True).unlink()

    def create_inventory_revaluation_price_change_average(self):
        revaluation_type = 'price_change'
        # Create an Inventory Revaluation for average cost product
        invent_price_change_average = self._create_inventory_revaluation(
            revaluation_type,
            self.product_average_1)
        invent_price_change_average.new_cost = 8.00
        return invent_price_change_average

    def test_inventory_revaluation_price_change_average(self):
        """Test that the inventory is revaluated when the
        inventory price for a product managed under average costing method is
        changed."""
        invent_price_change_average = \
            self.create_inventory_revaluation_price_change_average()
        # Post the inventory revaluation
        invent_price_change_average.button_post()
        expected_result = (10.00 - 8.00) * 10.00

        self.assertEqual(len(
            invent_price_change_average.account_move_ids[0].line_ids), 2,
            'Incorrect accounting entry generated')

        for move_line in \
                invent_price_change_average.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(move_line.credit, expected_result,
                                 'Incorrect inventory revaluation for '
                                 'Standard Product .')

        # Set the standard price and assert the amount changed
        context = {'active_model': u'product.product',
                   'active_ids': self.product_average_1.ids,
                   'active_id': self.product_average_1.id}

        self.product_average_1.with_context(context).\
            do_change_standard_price(5.00, self.account_revaluation.id)
        if self.product_average_1:
            self.assertEqual(self.product_average_1.standard_price, 5.0,
                             'Incorrect Product Price.')

    def create_inventory_revaluation_value_change(self):
        # Create an Inventory Revaluation for value change for average
        # cost product
        revaluation_type = 'inventory_value'
        invent_value_change = self._create_inventory_revaluation(
            revaluation_type,
            self.product_average_1)
        invent_value_change.new_value = 100.00
        return invent_value_change

    def test_inventory_revaluation_value_change(self):
        """Test that the inventory is revaluated when the
        inventory price for any product is changed."""
        invent_value_change = self.create_inventory_revaluation_value_change()
        # Post the inventory revaluation
        invent_value_change.button_post()

        self.assertEqual(len(
            invent_value_change.account_move_ids[0].line_ids), 2,
            'Incorrect accounting entry generated')

        with self.assertRaises(exceptions.Warning):
            invent_value_change.account_move_ids.unlink()

        with self.assertRaises(exceptions.Warning):
            invent_value_change.account_move_ids[0].line_ids.unlink()

        for move_line in invent_value_change.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(move_line.credit, 50.0,
                                 'Incorrect inventory revaluation for '
                                 'type Inventory Debit/Credit.')

    def test_mass_post(self):
        """Test mass post"""
        revaluations = self.env['stock.inventory.revaluation']

        # Create an Inventory Revaluation for average cost product
        invent_price_change_average = \
            self.create_inventory_revaluation_price_change_average()
        revaluations += invent_price_change_average

        # Create an Inventory Revaluation for real cost product
        invent_value_change = self.create_inventory_revaluation_value_change()
        revaluations += invent_value_change

        # Post the inventory revaluation using wizard
        self._mass_post(revaluations)

        # Check that both inventory valuations are now posted
        self.assertEqual(invent_price_change_average.state, 'posted')
        self.assertEqual(invent_value_change.state, 'posted')

    def test_cancel(self):
        """Test cancel"""
        # Create an Inventory Revaluation for real cost product
        revaluation_type = 'price_change'
        invent_price_change_real = \
            self._create_inventory_revaluation(
                revaluation_type,
                self.product_real_1)

        # Create an Inventory Revaluation Line Quant
        date_from = date.today() - timedelta(1)
        self._get_quant(date_from, invent_price_change_real)

        invent_price_change_real.sudo(self.user1).button_post()

        # Allow cancelling journal entries
        invent_price_change_real.journal_id.sudo().update_posted = True

        # Cancel the inventory revaluation
        invent_price_change_real.sudo(self.user1).button_cancel()

        for reval_quant in invent_price_change_real.reval_quant_ids:
            self.assertEqual(reval_quant.quant_id.cost, 10.0,
                             'Cancelling a revaluation does not restore the '
                             'original quant cost.')

        self.assertEqual(len(
            invent_price_change_real.account_move_ids), 0,
            'Accounting entries have not been removed after cancel')

    def test_inventory_revaluation_price_change_real_multi_quant(self):
        """Test that the inventory is revaluated when the
        inventory price for a product managed under real costing method is
        changed even if they are multple quant to revaluate"""
        # Create an Inventory Revaluation for real cost product

        location = self.env.ref('stock.stock_location_components')
        self._update_product_qty(self.product_real_1, location, 1)

        revaluation_type = 'price_change'
        invent_price_change_real = \
            self._create_inventory_revaluation(
                revaluation_type,
                self.product_real_1)

        # Create an Inventory Revaluation Line Quant
        date_from = date.today() - timedelta(1)
        self._get_quant(date_from, invent_price_change_real)

        invent_price_change_real.sudo(self.user1).button_post()

        expected_result = (10.00 - 8.00) * 11.00
        self.assertEqual(len(
            invent_price_change_real.account_move_ids[0].line_ids), 2,
            'Incorrect accounting entry generated')

        for move_line in invent_price_change_real.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(move_line.credit, expected_result,
                                 'Incorrect inventory revaluation for '
                                 'type Price Change.')
