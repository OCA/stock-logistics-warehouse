# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tools import float_round
from datetime import datetime
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestStockInventoryForceDate(TransactionCase):

    def setUp(self):
        super(TestStockInventoryForceDate, self).setUp()
        # Models
        self.obj_wh = self.env['stock.warehouse']
        self.obj_location = self.env['stock.location']
        self.obj_inventory = self.env['stock.inventory']
        self.obj_product = self.env['product.product']
        self.obj_product_categ = self.env['product.category']
        self.obj_warehouse = self.env['stock.warehouse']
        self.obj_account = self.env['account.account']
        self.obj_upd_qty_wizard = self.env['stock.change.product.qty']
        # Refs
        self.picking_type_id = self.env.ref('stock.picking_type_out')
        self.loc_customer = self.env.ref('stock.stock_location_customers')
        # Records
        self.stock_input_account = self.obj_account.create({
            'name': 'Stock Input',
            'code': 'StockIn',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_liabilities').id,
        })
        self.stock_output_account = self.obj_account.create({
            'name': 'COGS',
            'code': 'cogs',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
        })
        self.stock_valuation_account = self.obj_account.create({
            'name': 'Stock Valuation',
            'code': 'Stock Valuation',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
        })
        self.expense_account = self.env['account.account'].create({
            'code': 'INVEXP',
            'name': 'inventory adjustments',
            'user_type_id':
            self.env.ref('account.data_account_type_expenses').id,
        })
        self.cost_change_account = self.env['account.account'].create({
            'code': 'COACC',
            'name': 'cost change',
            'user_type_id':
                self.env.ref('account.data_account_type_expenses').id,
        })
        self.stock_journal = self.env['account.journal'].create({
            'name': 'Stock Journal',
            'code': 'STJTEST',
            'type': 'general',
        })
        self.categ_standard = self.env['product.category'].create(
            {'name': 'STANDARD',
             'property_cost_method': 'standard',
             'property_valuation': 'real_time',
             'property_stock_account_input_categ_id':
                 self.stock_input_account.id,
             'property_stock_account_output_categ_id':
                 self.stock_output_account.id,
             'property_stock_valuation_account_id':
                 self.stock_valuation_account.id,
             'property_stock_journal': self.stock_journal.id,
             },
        )
        self.env.ref('stock.location_inventory').write({
            'valuation_in_account_id':
                self.expense_account.id,
            'valuation_out_account_id':
                self.expense_account.id,

        })
        self.product1 = self.obj_product.create({
            'name': 'Test Product 1',
            'type': 'product',
            'default_code': 'PROD1',
            'standard_price': 1.0,
            'categ_id': self.categ_standard.id,
        })
        self.product2 = self.obj_product.create({
            'name': 'Test Product 2',
            'type': 'product',
            'default_code': 'PROD2',
            'standard_price': 1.0,
            'categ_id': self.categ_standard.id,
        })
        self.test_loc = self.obj_location.create({
            'name': 'Test Location',
            'usage': 'internal',
        })
        self.test_bin = self.obj_location.create({
            'name': 'Test Bin Location',
            'usage': 'internal',
            'location_id': self.test_loc.id,
        })
        self.test_wh = self.obj_warehouse.create({
            'name': 'Test WH',
            'code': 'T',

        })
        self.obj_location._parent_store_compute()
        group_stock_man = self.env.ref('stock.group_stock_manager')
        self.manager = self.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'manager',
            'email': 'test.manager@example.com',
            'groups_id': [(6, 0, [group_stock_man.id])]
        })
        group_stock_user = self.env.ref('stock.group_stock_user')
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'user',
            'email': 'test.user@example.com',
            'groups_id': [(6, 0, [group_stock_user.id])]
        })
        self.env.user.company_id.standard_cost_change_account_id = \
            self.cost_change_account

    def test_01(self):
        """Tests if creating inventory adjustments in the past produce correct
        results forward in history.
        """
        # Create a fake history of changes to the standard price
        self.env['product.price.history'].create({
            'product_id': self.product1.id,
            'datetime': '2013-01-01 00:00:00',
            'cost': 100,
            'company_id': self.env.user.company_id.id,
        })
        self.env['product.price.history'].create({
            'product_id': self.product1.id,
            'datetime': '2014-01-01 00:00:00',
            'cost': 50,
            'company_id': self.env.user.company_id.id,
        })
        self.env['product.price.history'].create({
            'product_id': self.product1.id,
            'datetime': '2015-01-01 00:00:00',
            'cost': 25,
            'company_id': self.env.user.company_id.id,
        })
        to_date = '2013-02-01 00:00:00'
        inventory = self.obj_inventory.create({
            'name': 'Test past date',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'force_inventory_date': True,
            'date': to_date,
            'accounting_date': to_date,
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 1.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        inventory.action_validate()
        # Check that the stock valuation is correct
        price_used = self.product1.get_history_price(
            self.env.user.company_id.id,
            date=to_date,
        )
        qty_available = self.product1.with_context(
            company_owned=True, owner_id=False, to_date=to_date).qty_available
        value = price_used * qty_available
        round_curr = self.env.user.company_id.currency_id.rounding
        inventory_valuation = float_round(value, precision_rounding=round_curr)
        # Check that the accounting valuation for this product is correct
        accounting_valuation = sum(self.env['account.move.line'].search([
            ('account_id', '=', self.stock_valuation_account.id),
            ('product_id', '=', self.product1.id),
            ('date', '<=', '2013-04-01'),
        ]).mapped('balance'))
        self.assertEqual(inventory_valuation, accounting_valuation)
        self.assertEqual(inventory_valuation, 100.00)
        # Check in 2014
        to_date = '2014-02-01 00:00:00'
        # Check that the stock valuation is correct
        price_used = self.product1.get_history_price(
            self.env.user.company_id.id,
            date=to_date,
        )
        qty_available = self.product1.with_context(
            company_owned=True, owner_id=False, to_date=to_date).qty_available
        value = price_used * qty_available
        round_curr = self.env.user.company_id.currency_id.rounding
        inventory_valuation = float_round(value, precision_rounding=round_curr)
        # Check that the accounting valuation for this product is correct
        accounting_valuation = sum(self.env['account.move.line'].search([
            ('account_id', '=', self.stock_valuation_account.id),
            ('product_id', '=', self.product1.id),
            ('date', '<=', '2014-04-01'),
        ]).mapped('balance'))
        self.assertEqual(inventory_valuation, accounting_valuation)
        self.assertEqual(inventory_valuation, 50.00)
        # Check that the current quantity available is 1
        qty_available = self.product1.with_context(
            company_owned=True, owner_id=False).qty_available
        self.assertEqual(qty_available, 1.00)
        # Check in 2015
        to_date = '2015-02-01 00:00:00'
        # Check that the stock valuation is correct
        price_used = self.product1.get_history_price(
            self.env.user.company_id.id,
            date=to_date,
        )
        qty_available = self.product1.with_context(
            company_owned=True, owner_id=False, to_date=to_date).qty_available
        value = price_used * qty_available
        round_curr = self.env.user.company_id.currency_id.rounding
        inventory_valuation = float_round(value, precision_rounding=round_curr)
        # Check that the accounting valuation for this product is correct
        accounting_valuation = sum(self.env['account.move.line'].search([
            ('account_id', '=', self.stock_valuation_account.id),
            ('product_id', '=', self.product1.id),
            ('date', '<=', '2015-04-01'),
        ]).mapped('balance'))
        self.assertEqual(inventory_valuation, accounting_valuation)
        self.assertEqual(inventory_valuation, 25.00)
        # Check that the stock move line has the correct date
        ml = self.env['stock.move.line'].search([
            ('product_id', '=', self.product1.id),
            ('date', '=', '2013-02-01 00:00:00')
        ])
        self.assertEqual(len(ml), 1)

    def test_02(self):
        """Test that we cannot post an inventory before the lock date.
        """
        self.env.user.company_id.force_inventory_lock_date = '2015-01-01'
        to_date = datetime(2013, 2, 1, 0, 0, 0, 0)
        inventory = self.obj_inventory.create({
            'name': 'Test past date',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'force_inventory_date': True,
            'date': to_date,
            'accounting_date': to_date.date(),
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 1.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        with self.assertRaises(ValidationError):
            inventory.action_validate()

    def test_03(self):
        to_date = datetime(2013, 2, 1, 0, 0, 0, 0)
        self.env['product.price.history'].create({
            'product_id': self.product1.id,
            'datetime': to_date,
            'cost': 25,
            'company_id': self.env.user.company_id.id,
        })
        inventory = self.obj_inventory.create({
            'name': 'Test past date',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'force_inventory_date': True,
            'date': to_date,
            'accounting_date': to_date.date(),
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 100.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        inventory.action_validate()
        picking = self.env['stock.picking'].with_context(
        ).create({
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.test_loc.id,
            'location_dest_id': self.loc_customer.id
        })
        move = self.env['stock.move'].create({
            'name': 'Test Move',
            'product_id': self.product1.id,
            'product_uom_qty': 50.0,
            'product_uom': self.product1.uom_id.id,
            'picking_id': picking.id,
            'state': 'draft',
            'location_id': self.test_loc.id,
            'location_dest_id': self.loc_customer.id,
        })
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(move.reserved_availability, 50.0)
        self.env['product.price.history'].create({
            'product_id': self.product1.id,
            'datetime': '2013-01-01 00:00:00',
            'cost': 100,
            'company_id': self.env.user.company_id.id,
        })
        self.env['product.price.history'].create({
            'product_id': self.product1.id,
            'datetime': '2014-01-01 00:00:00',
            'cost': 50,
            'company_id': self.env.user.company_id.id,
        })
        inventory = self.obj_inventory.create({
            'name': 'Test past date',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'force_inventory_date': True,
            'date': to_date,
            'accounting_date': to_date.date(),
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 0.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        inventory.action_validate()
        self.assertEqual(move.reserved_availability, 0.0)

    def test_04(self):
        # Test introducing 100 units in the past and adjusting to 0 today.
        # If we make then an inventory adjustment again in the past the
        # theoretical quantity should be 100.
        to_date = datetime(2013, 2, 1, 0, 0, 0, 0)
        self.env['product.price.history'].create({
            'product_id': self.product1.id,
            'datetime': to_date,
            'cost': 25,
            'company_id': self.env.user.company_id.id,
        })
        inventory = self.obj_inventory.create({
            'name': 'Test past date',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'force_inventory_date': True,
            'date': to_date,
            'accounting_date': to_date.date(),
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 100.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        inventory.action_validate()
        inventory = self.obj_inventory.create({
            'name': 'Test past date',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 0.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        inventory.action_validate()
        inventory = self.obj_inventory.create({
            'name': 'Test past date',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'force_inventory_date': True,
            'date': to_date,
            'accounting_date': to_date.date(),
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 0.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        qty_available = self.product1.with_context(
            company_owned=True, owner_id=False, to_date=to_date).qty_available
        inventory.action_start()
        # Check that the quantity back then is correct
        for line in inventory.line_ids.filtered(
                lambda l: l.product_id == self.product1):
            self.assertEqual(line.theoretical_qty, qty_available)
            self.assertEqual(line.theoretical_qty, 100)

    def test_onchange_accounting_date(self):
        to_date = datetime(2013, 2, 1, 0, 0, 0, 0)
        inventory = self.obj_inventory.create({
            'name': 'Test past date',
            'location_id': self.test_loc.id,
            'filter': 'none',
            'force_inventory_date': True,
            'date': to_date,
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 0.0,
                    'location_id': self.test_loc.id,
                }),
            ],
        })
        inventory._onchange_force_inventory_date()
        self.assertEqual(inventory.accounting_date, to_date.date())
