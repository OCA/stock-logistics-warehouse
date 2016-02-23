# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime
from datetime import date, timedelta


class TestStockInventoryRevaluation(TransactionCase):
    """Test that the Inventory is Revaluated when the
    inventory price for any product is changed."""

    def setUp(self):
        super(TestStockInventoryRevaluation, self).setUp()
        # Get required Model
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']
        self.reval_model = self.env['stock.inventory.revaluation']
        self.reval_line_model = self.env['stock.inventory.revaluation.line']
        self.account_model = self.env['account.account']
        self.acc_type_model = self.env['account.account.type']
        self.reval_line_quant_model = self.\
            env['stock.inventory.revaluation.line.quant']
        self.get_quant_model = self.\
            env['stock.inventory.revaluation.line.get.quant']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.stock_lot_model = self.env['stock.production.lot']
        self.stock_location_model = self.env['stock.location']
        # Get required Model data
        self.fixed_account = self.env.ref('account.xfa')
        self.purchased_stock = self.env.ref('account.stk')
        self.debtors_account = self.env.ref('account.a_recv')
        self.cash_account = self.env.ref('account.cash')
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.journal = self.env.ref('account.miscellaneous_journal')
        self.company = self.env.ref('base.main_company')

        location = self.stock_location_model.search([('name', '=', 'WH')])
        self.location = self.stock_location_model.search([('location_id', '=',
                                                           location.id)])

        # Create account for Goods Received Not Invoiced
        name = 'Goods Received Not Invoiced'
        code = 'grni'
        acc_type = 'equity'
        self.account_grni = self._create_account(acc_type, name, code,
                                                 self.company)
        # Create account for Cost of Goods Sold
        name = 'Cost of Goods Sold'
        code = 'cogs'
        acc_type = 'expense'
        self.account_cogs = self._create_account(acc_type, name, code,
                                                 self.company)

        # Create account for Inventory
        name = 'Inventory'
        code = 'inventory'
        acc_type = 'asset'
        self.account_inventory = self._create_account(acc_type, name, code,
                                                      self.company)

        # Create account for Inventory Revaluation
        name = 'Inventory Revaluation'
        code = 'revaluation'
        acc_type = 'expense'
        self.account_revaluation = self._create_account(acc_type, name, code,
                                                        self.company)

        # Create product category
        self.product_ctg = self._create_product_category()

        # Create a Product with real cost
        standard_price = 10.0
        list_price = 20.0
        self.product_real = self._create_product('real', standard_price,
                                                 list_price)
        # Add default quantity
        quantity = 20.00
        self._update_product_qty(self.product_real, self.location, quantity)

        # Create a Product with average cost
        standard_price = 10.0
        list_price = 20.0
        self.product_average = self._create_product('average', standard_price,
                                                    list_price)

        # Add default quantity
        quantity = 20.00
        self._update_product_qty(self.product_average, self.location, quantity)

    def _create_account(self, acc_type, name, code, company):
        """Create an account."""
        type_ids = self.acc_type_model.search([('code', '=', acc_type)])
        account = self.account_model.create({
            'name': name,
            'code': code,
            'type': 'other',
            'user_type': type_ids.ids and type_ids.ids[0],
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

    def _create_product(self, cost_method, standard_price, list_price):
        """Create a Product with inventory valuation set to auto."""
        product = self.product_model.create({
            'name': 'test_product',
            'categ_id': self.product_ctg.id,
            'type': 'product',
            'standard_price': standard_price,
            'list_price': list_price,
            'valuation': 'real_time',
            'cost_method': cost_method,
            'property_stock_account_input': self.account_grni.id,
            'property_stock_account_output': self.account_cogs.id,
        })
        return product

    def _create_inventory_revaluation(self, journal, revaluation_type):
        """Create a Inventory Revaluation with revaluation_type set to
         price_change to recalculate inventory value according to new price."""
        inventory = self.reval_model.create({
            'name': 'test_inventory_revaluation',
            'document_date': datetime.today(),
            'revaluation_type': revaluation_type,
            'journal_id': journal.id,
        })
        return inventory

    def _create_inventory_revaluation_line(self, revaluation, product):
        """Create a Inventory Revaluation line by applying
         increase and decrease account to it."""
        self.increase_account_id = product.categ_id and \
            product.categ_id.\
            property_inventory_revaluation_increase_account_categ
        self.decrease_account_id = product.categ_id and \
            product.categ_id.\
            property_inventory_revaluation_decrease_account_categ

        line = self.reval_line_model.create({
            'product_template_id': product.id,
            'revaluation_id': revaluation.id,
            'increase_account_id': self.increase_account_id.id,
            'decrease_account_id': self.decrease_account_id.id,
        })
        return line

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        product_qty = self.stock_change_model.create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def _get_quant(self, date_from, line):
        """Get Quants for Inventory Revaluation between the date supplied."""
        quant = self.get_quant_model.create({
            'date_from': date_from,
            'date_to': datetime.today(),
        })
        line_context = {
            'active_id': line.id,
            'active_ids': line.ids,
            'active_model': 'stock.inventory.revaluation.line',
        }
        quant.with_context(line_context).process()
        for line_quant in line.line_quant_ids:
            line_quant.new_cost = 8.0

    def test_inventory_revaluation_price_change(self):
        """Test that the inventory is revaluated when the
        inventory price for any product is changed."""

        # Create an Inventory Revaluation
        revaluation_type = 'price_change'
        invent_price_change = self._create_inventory_revaluation(
            self.journal, revaluation_type)

        # Create an Inventory Revaluation Line for real cost product
        invent_line_real = \
            self._create_inventory_revaluation_line(
                invent_price_change, self.product_real.product_tmpl_id)

        # Create an Inventory Revaluation Line Quant
        date_from = date.today() - timedelta(1)
        self._get_quant(date_from, invent_line_real)

        # Create an Inventory Revaluation Line for average cost product
        invent_line_avg = self._create_inventory_revaluation_line(
            invent_price_change, self.product_average.product_tmpl_id)
        # Post the inventory revaluation
        invent_line_avg.new_cost = 8.00

        invent_price_change.button_post()

        expected_result = (10.00 - 8.00) * 20.00
        for line in invent_price_change.line_ids:
            for move_line in line.move_id.line_id:
                if move_line.debit:
                    self.assertEqual(move_line.debit, expected_result,
                                     'Incorrect inventory revaluation for '
                                     'type Price Change.')

    def test_inventory_revaluation_value_change(self):
        """Test that the inventory is revaluated when the
        inventory price for any product is changed."""
        # Create an Inventory Revaluation for value change
        revaluation_type = 'inventory_value'
        invent_inventory_value = self._create_inventory_revaluation(
            self.journal, revaluation_type)

        # Create an Inventory Revaluation Line for average cost product
        invent_line_average = self._create_inventory_revaluation_line(
            invent_inventory_value, self.product_average.product_tmpl_id)
        invent_line_average.new_value = 100.00

        # Post the inventory revaluation
        invent_inventory_value.button_post()

        for line in invent_inventory_value.line_ids:
            for move_line in line.move_id.line_id:
                if move_line.debit:
                    self.assertEqual(move_line.debit, 100.0,
                                     'Incorrect inventory revaluation for '
                                     'type Inventory Debit/Credit.')
