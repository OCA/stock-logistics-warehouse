# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        self.reval_line_quant_model = self.\
            env['stock.inventory.revaluation.line.quant']
        self.get_quant_model = self.\
            env['stock.inventory.revaluation.line.get.quant']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.stock_lot_model = self.env['stock.production.lot']
        self.stock_location_model = self.env['stock.location']
        self.stock_history_model = self.env['stock.history']
        # Get required Model data
        self.fixed_account = self.env.ref('account.xfa')
        self.purchased_stock = self.env.ref('account.stk')
        self.debtors_account = self.env.ref('account.a_recv')
        self.cash_account = self.env.ref('account.cash')
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.journal = self.env.ref('account.miscellaneous_journal')

        location = self.stock_location_model.search([('name', '=', 'WH')])
        self.location = self.stock_location_model.search([('location_id', '=',
                                                           location.id)])
        # Create a Product
        standard_price = 10.0
        list_price = 20.0
        self.product = self._create_product(standard_price, list_price)
        # Create an Inventory Revaluation
        revaluation_type = 'price_change'
        self.invent = self._create_inventory_revaluation(self.journal,
                                                         revaluation_type)
        # Create an Inventory Revaluation Line
        self.invent_line = self.\
            _create_inventory_revaluation_line(self.product.product_tmpl_id.id)
        # Create an Inventory Revaluation Line
        quantity = 20.00
        self.updated_qty = self._update_product_qty(self.product,
                                                    self.location, quantity)
        # Create an Inventory Revaluation Line Quant
        date_from = date.today() - timedelta(1)
        self.get_quant = self._get_quant(date_from, self.invent,
                                         self.invent_line)
        # Update Inventory Price for the product
        new_cost = 8.0
        self.update_cost = self._update_cost(new_cost, self.invent,
                                             self.invent_line, self.product)

    def _create_product(self, standard_price, list_price):
        """Create a Product with inventory valuation set to auto."""
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.purchased_stock.id,
            'property_inventory_revaluation_increase_account_categ':\
                self.fixed_account.id,
            'property_inventory_revaluation_decrease_account_categ':\
                self.purchased_stock.id,
        })
        product = self.product_model.create({
            'name': 'test_product',
            'categ_id': product_ctg.id,
            'type': 'product',
            'uom_id': self.product_uom.id,
            'standard_price': standard_price,
            'list_price': list_price,
            'valuation': 'real_time',
            'cost_method': 'real',
            'property_stock_account_input': self.debtors_account.id,
            'property_stock_account_output': self.cash_account.id,
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

    def _create_inventory_revaluation_line(self, product):
        """Create a Inventory Revaluation line by applying
         increase and decrease account to it."""
        self.increase_account_id = self.product.categ_id and \
            self.product.categ_id.\
            property_inventory_revaluation_increase_account_categ
        self.decrease_account_id = self.product.categ_id and \
            self.product.categ_id.\
            property_inventory_revaluation_decrease_account_categ

        line = self.reval_line_model.create({
            'product_template_id': product,
            'revaluation_id': self.invent.id,
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

    def _get_quant(self, date, invent, line):
        """Get Quants for Inventory Revaluation between the date supplied."""
        quant = self.get_quant_model.create({
            'date_from': date,
            'date_to': datetime.today(),
        })
        line_context = {
            'active_id': line.id,
            'active_ids': line.ids,
            'active_model': 'stock.inventory.revaluation.line',
        }
        quant.with_context(line_context).process()
        return quant

    def _update_cost(self, new_cost, invent, line, product):
        """Update Inventory Price for the product and
        recalculate the Inventory Value."""
        history = self.stock_history_model.search([('product_id', 'in',
                                                    [product.id])])
        self.old_value = history.inventory_value
        line.line_quant_ids.write({'new_cost': new_cost})
        invent.button_post()
        history.refresh()
        self.new_value = history.inventory_value
        return True

    def test_inventory_revaluation(self):
        """Test that the inventory is revaluated when the
        inventory price for any product is changed."""
        self.assertNotEqual(self.old_value, self.new_value,
                            'Inventory is not recalculated as per new value!')
