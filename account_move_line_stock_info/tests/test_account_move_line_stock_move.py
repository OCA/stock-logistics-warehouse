# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestAccountMoveLineStockInfo(common.TransactionCase):

    def setUp(self):
        super(TestAccountMoveLineStockInfo, self).setUp()
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']
        self.acc_type_model = self.env['account.account.type']
        self.account_model = self.env['account.account']
        self.aml_model = self.env['account.move.line']
        self.stock_picking_model = self.env['stock.picking']
        self.stock_move_model = self.env['stock.move']
        self.res_users_model = self.env['res.users']

        self.partner1 = self.env.ref('base.res_partner_1')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.location_supplier = self.env.ref('stock.stock_location_suppliers')
        self.location_customer = self.env.ref('stock.stock_location_customers')
        self.company = self.env.ref('base.main_company')
        self.picking_type_in = self.env.ref('stock.picking_type_in')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.group_stock_user = self.env.ref('stock.group_stock_user')
        self.group_account_invoice = self.env.ref(
            'account.group_account_invoice')
        self.group_account_manager = self.env.ref(
            'account.group_account_manager')

        # Create account for Goods Received Not Invoiced
        acc_type = 'equity'
        name = 'Goods Received Not Invoiced'
        code = 'grni'
        self.account_grni = self._create_account(acc_type, name, code,
                                                 self.company)

        # Create account for Cost of Goods Sold
        acc_type = 'expense'
        name = 'Cost of Goods Sold'
        code = 'cogs'
        self.account_cogs = self._create_account(acc_type, name, code,
                                                 self.company)
        # Create account for Inventory
        acc_type = 'asset'
        name = 'Inventory'
        code = 'inventory'
        self.account_inventory = self._create_account(acc_type, name, code,
                                                      self.company)
        # Create Product
        self.product = self._create_product()
        # company

        # Create users
        self.stock_user = self._create_user('stock_user',
                                            [self.group_stock_user,
                                             self.group_account_invoice],
                                            self.company)
        self.account_invoice = self._create_user('account_invoice',
                                                 [self.group_account_invoice],
                                                 self.company)
        self.account_manager = self._create_user('account_manager',
                                                 [self.group_account_manager],
                                                 self.company)

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            self.res_users_model.with_context(
                {'no_reset_password': True}).create({
                    'name': 'Test User',
                    'login': login,
                    'password': 'demo',
                    'email': 'test@yourcompany.com',
                    'company_id': company.id,
                    'company_ids': [(4, company.id)],
                    'groups_id': [(6, 0, group_ids)]
                })
        return user.id

    def _create_account(self, acc_type, name, code, company):
        """Create an account."""
        types = self.acc_type_model.search([('code', '=', acc_type)])
        account = self.account_model.create({
            'name': name,
            'code': code,
            'type': 'other',
            'user_type': types and types[0].id,
            'company_id': company.id
        })
        return account

    def _create_product(self):
        """Create a Product."""
#        group_ids = [group.id for group in groups]
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.account_inventory.id
        })
        product = self.product_model.create({
            'name': 'test_product',
            'categ_id': product_ctg.id,
            'type': 'product',
            'standard_price': 1.0,
            'list_price': 1.0,
            'valuation': 'real_time',
            'property_stock_account_input': self.account_grni.id,
            'property_stock_account_output': self.account_cogs.id,
        })
        return product

    def _create_picking(self, picking_type, location, location_dest):

        picking = self.stock_picking_model.sudo(self.stock_user).create({
            'picking_type_id': picking_type.id,
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.product.id,
                    'product_uom': self.product.uom_id.id,
                    'product_uom_qty': 3,
                    'location_id': location.id,
                    'location_dest_id': location_dest.id,
                    'price_unit': 10
                })]
        })
        return picking

    def test_account_move_line_stock_move(self):
        """Test that processing an incoming picking the account moves
        generated by the picking moves will contain the stock move.
        """
        picking_in = self._create_picking(
            self.picking_type_in, self.location_supplier, self.location_stock)
        picking_in.action_confirm()
        picking_in.action_done()

        account_move_line = False
        for move in picking_in.move_lines:
            self.assertEqual(len(move.account_move_line_ids), 2)
            for aml in move.account_move_line_ids:
                self.assertEqual(aml.name, move.name)
                account_move_line = aml

        picking_out = self._create_picking(
            self.picking_type_out, self.location_supplier, self.location_stock)
        picking_out.action_confirm()
        picking_out.action_done()

        for move in picking_out.move_lines:
            self.assertEqual(len(move.account_move_line_ids), 2)
            for aml in move.account_move_line_ids:
                self.assertEqual(aml.name, move.name)

        # Test that the account invoice user can access to the stock info
        self.assertEqual(account_move_line.sudo(
            self.account_invoice).stock_move_id.name,
            account_move_line.sudo(self.account_invoice).name)

        # Test that the account manager can access to the stock info
        self.assertEqual(account_move_line.sudo(
            self.account_manager).stock_move_id.name,
            account_move_line.sudo(self.account_manager).name)
