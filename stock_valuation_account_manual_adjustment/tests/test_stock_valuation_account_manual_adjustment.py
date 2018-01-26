# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import fields
import time


class TestProductInventoryAccountReconcile(TransactionCase):
    """Test that the Inventory is Revaluated when the
    inventory price for any product is changed."""

    def setUp(self):
        super(TestProductInventoryAccountReconcile, self).setUp()
        # Get required Model
        self.product_model = self.env['product.product']
        self.template_model = self.env['product.template']
        self.product_ctg_model = self.env['product.category']
        self.account_model = self.env['account.account']
        self.acc_type_model = self.env['account.account.type']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.stock_lot_model = self.env['stock.production.lot']
        self.stock_location_model = self.env['stock.location']
        self.account_move_model = self.env['account.move']
        self.account_move_line_model = self.env['account.move.line']
        # Get required Model data
        self.company = self.env.ref('base.main_company')

        location = self.stock_location_model.search([('name', '=', 'WH')])
        self.location = self.stock_location_model.search([('location_id', '=',
                                                           location.id)])

        # Account types
        expense_type = self.env.ref('account.data_account_type_expenses')
        equity_type = self.env.ref('account.data_account_type_equity')
        asset_type = self.env.ref('account.data_account_type_fixed_assets')

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
        # Create a Product with average cost
        standard_price = 10.0
        list_price = 20.0
        self.product_average_1 = self._create_product('average',
                                                      standard_price,
                                                      False,
                                                      list_price)
        # Add default quantity
        quantity = 10.00
        self._update_product_qty(self.product_average_1, self.location,
                                 quantity)

        # Default journal
        journals = self.env['account.journal'].search([('type', '=',
                                                       'general')])
        self.journal = journals[0]

        # Create a journal entry
        self.move = self._create_account_move(100)

    def _create_account(self, acc_type, name, code, company):
        """Create an account."""
        account = self.account_model.create({
            'name': name,
            'code': code,
            'user_type_id': acc_type.id,
            'company_id': company.id
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
                'property_stock_account_output': self.account_cogs.id
            })
            return template.product_variant_ids[0]
        product = self.product_model.create(
            {'product_tmpl_id': template.id,
             'list_price': list_price})
        return product

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        product_qty = self.stock_change_model.create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def _create_account_move(self, amount):
        date_move = fields.Date.today()

        debit_data = [(0, 0, {
            'name': self.product_average_1.name,
            'date': date_move,
            'product_id': self.product_average_1.id,
            'account_id': self.account_inventory.id,
            'debit': amount
        })]
        credit_data = [(0, 0, {
            'name': self.product_average_1.name,
            'date': date_move,
            'product_id': self.product_average_1.id,
            'account_id': self.account_revaluation.id,
            'credit': amount
        })]
        line_data = debit_data + credit_data
        move = self.account_move_model.create({
            'date': time.strftime('%Y-%m-%d'),
            'ref': 'Sample',
            'journal_id': self.journal.id,
            'line_ids': line_data
        })
        return move

    def test_reconcile_product(self):
        """Test that it is possible to reconcile for a product"""
        self.assertEquals(self.product_average_1.valuation_discrepancy, -100.0)

        wiz = self.env['stock.valuation.account.mass.adjust'].with_context(
            active_model="product.product",
            active_ids=[self.product_average_1.id],
            active_id=self.product_average_1.id).create({
                'increase_account_id': self.account_revaluation.id,
                'decrease_account_id': self.account_revaluation.id,
                'journal_id': self.journal.id,
                'remarks': 'Test'
                })
        wiz.process()
        self.product_average_1.refresh()
        self.assertEquals(self.product_average_1.valuation_discrepancy, 0.0)
