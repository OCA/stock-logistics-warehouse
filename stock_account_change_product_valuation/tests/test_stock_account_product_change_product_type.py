# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockAccountChangeProductValuation(TransactionCase):
    """Test that the Inventory is Revaluated when the
    inventory price for any product is changed."""

    def setUp(self):
        super(TestStockAccountChangeProductValuation, self).setUp()
        # Get required Model
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']
        self.account_model = self.env['account.account']
        self.acc_type_model = self.env['account.account.type']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.stock_lot_model = self.env['stock.production.lot']
        self.stock_location_model = self.env['stock.location']
        self.stock_quant_model = self.env['stock.quant']
        # Get required Model data
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.company = self.env.ref('base.main_company')
        self.location_supplier = self.env.ref('stock.stock_location_suppliers')

        location = self.stock_location_model.search([('name', '=', 'WH')])
        self.location = self.stock_location_model.search([('location_id', '=',
                                                           location.id)])

        # Create account for Goods Received Not Invoiced
        name = 'Goods Received Not Invoiced'
        code = 'grni'
        acc_type = 'Equity'
        self.account_grni = self._create_account(acc_type, name, code,
                                                 self.company)
        # Create account for Cost of Goods Sold
        name = 'Cost of Goods Sold'
        code = 'cogs'
        acc_type = 'Expenses'
        self.account_cogs = self._create_account(acc_type, name, code,
                                                 self.company)

        # Create account for Inventory
        name = 'Inventory'
        code = 'inventory'
        acc_type = 'Current Assets'
        self.account_inventory = self._create_account(acc_type, name, code,
                                                      self.company)
        # Create product category
        self.product_ctg = self._create_product_category()

    def _create_account(self, acc_type, name, code, company):
        """Create an account."""
        type_ids = self.acc_type_model.search([('name', '=', acc_type)])
        account = self.account_model.create({
            'name': name,
            'code': code,
            'user_type_id': type_ids.ids and type_ids.ids[0],
            'company_id': company.id
        })
        return account

    def _create_product_category(self):
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.account_inventory.id,
        })
        return product_ctg

    def _create_product(self, type, cost_method, standard_price, list_price):
        """Create a Product with inventory valuation set to auto."""
        product = self.product_model.create({
            'name': 'test_product',
            'categ_id': self.product_ctg.id,
            'type': type,
            'standard_price': standard_price,
            'list_price': list_price,
            'valuation': 'real_time',
            'cost_method': cost_method,
            'property_stock_account_input': self.account_grni.id,
            'property_stock_account_output': self.account_cogs.id,
        })
        return product

    def create_move(self, product, source_location, destination_location,
                    cost):
        move = self.env['stock.move'].create({
            'name': 'Test move',
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 10,
            'price_unit': cost,
            'location_id': source_location.id,
            'location_dest_id': destination_location.id}
        )
        return move

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        product_qty = self.stock_change_model.create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def test_consumable_to_stockable_standard(self):
        """Test that the cost of quants is reset and the unit cost of the
        product is 0"""
        # Create a Product of type consumable
        standard_price = 10.0
        list_price = 20.0
        product_consu_standard = self._create_product(
            'consu', 'standard', standard_price, list_price)

        # Add default quantity
        quantity = 20.00
        self._update_product_qty(product_consu_standard, self.location,
                                 quantity)

        product_consu_standard.type = 'product'
        quants = self.stock_quant_model.search([('product_id', '=',
                                                 product_consu_standard.id)])
        for quant in quants:
            self.assertEquals(quant.cost, 0.0, 'Quants still have cost')
            self.assertEquals(product_consu_standard.standard_price,
                              0.0, 'Standard price is not 0')

    def test_consumable_to_stockable_average(self):
        """Test that the cost of quants is reset and the unit cost of the
        product is 0"""
        # Create a Product of type consumable
        standard_price = 10.0
        list_price = 20.0
        product = self._create_product('consu', 'average', standard_price,
                                       list_price)

        # Add default quantity
        quantity = 20.00
        self._update_product_qty(product, self.location,
                                 quantity)

        product.type = 'product'
        quants = self.stock_quant_model.search([('product_id', '=',
                                                 product.id)])
        for quant in quants:
            self.assertEquals(quant.cost, 0.0, 'Quants still have cost')
            self.assertEquals(product.standard_price, 0.0,
                              'Standard price is not 0')

    def test_stockable_average_to_real(self):
        """Test that the cost of quants is reset and the unit cost of the
        product is 0"""
        # Create a Product of type consumable
        standard_price = 10.0
        list_price = 20.0
        product = self._create_product('product', 'average', 0.0, list_price)

        move_in_1 = self.create_move(product, self.location_supplier,
                                     self.location, standard_price)
        move_in_1.action_done()

        move_in_2 = self.create_move(product, self.location_supplier,
                                     self.location, standard_price*2)
        move_in_2.action_done()

        product.cost_method = 'real'
        quants = self.stock_quant_model.search([('product_id', '=',
                                                 product.id)])
        for quant in quants:
            self.assertEquals(quant.cost, product.standard_price,
                              'Quants do not have cost as the product '
                              'standard price')

    def test_stockable_real_to_average(self):
        """Test that the product standard price is now the average of the
        inventory value of the internal quants"""
        # Create a Product of type consumable
        standard_price = 10.0
        list_price = 20.0
        product = self._create_product(
            'product', 'real', 0.0, list_price)

        move_in_1 = self.create_move(product, self.location_supplier,
                                     self.location, standard_price)
        move_in_1.action_done()

        move_in_2 = self.create_move(product, self.location_supplier,
                                     self.location, standard_price*2)
        move_in_2.action_done()

        product.cost_method = 'average'

        self.assertEquals(product.standard_price, 15,
                          'Product has no correct standard price after '
                          'changing costing method from real to average')
