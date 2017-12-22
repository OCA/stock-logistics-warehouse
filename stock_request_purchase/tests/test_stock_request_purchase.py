# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestStockRequestPurchase(common.TransactionCase):

    def setUp(self):
        super(TestStockRequestPurchase, self).setUp()

        # common models
        self.stock_request = self.env['stock.request']

        # refs
        self.stock_request_user_group = \
            self.env.ref('stock_request.group_stock_request_user')
        self.stock_request_manager_group = \
            self.env.ref('stock_request.group_stock_request_manager')
        self.main_company = self.env.ref('base.main_company')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.categ_unit = self.env.ref('product.product_uom_categ_unit')

        # common data
        self.company_2 = self.env['res.company'].create({
            'name': 'Comp2',
        })
        self.wh2 = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_2.id)], limit=1)
        self.stock_request_user = self._create_user(
            'stock_request_user',
            [self.stock_request_user_group.id],
            [self.main_company.id, self.company_2.id])
        self.stock_request_manager = self._create_user(
            'stock_request_manager',
            [self.stock_request_manager_group.id],
            [self.main_company.id, self.company_2.id])
        self.route_buy = self.warehouse.buy_pull_id.route_id
        self.supplier = self.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })
        self.product = self._create_product('SH', 'Shoes', False)

        self.uom_dozen = self.env['product.uom'].create({
            'name': 'Test-DozenA',
            'category_id': self.categ_unit.id,
            'factor_inv': 12,
            'uom_type': 'bigger',
            'rounding': 0.001})

    def _create_user(self, name, group_ids, company_ids):
        return self.env['res.users'].with_context(
            {'no_reset_password': True}).create(
            {'name': name,
             'password': 'demo',
             'login': name,
             'email': '@'.join([name, '@test.com']),
             'groups_id': [(6, 0, group_ids)],
             'company_ids': [(6, 0, company_ids)]
             })

    def _create_product(self, default_code, name, company_id):
        return self.env['product.product'].create({
            'name': name,
            'default_code': default_code,
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'company_id': company_id,
            'type': 'product',
            'route_ids': [(6, 0, self.route_buy.ids)],
            'seller_ids': [(0, 0, {'name': self.supplier.id, 'delay': 5})]
        })

    def test_create_request_01(self):
        """Single Stock request with buy rule"""
        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 5.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }

        stock_request = self.stock_request.sudo(
            self.stock_request_user).create(vals)
        stock_request.action_confirm()

        self.assertEqual(stock_request.state, 'open')

        stock_request.refresh()

        self.assertEqual(len(stock_request.sudo().purchase_ids), 1)
        self.assertEqual(len(stock_request.picking_ids), 0)
        self.assertEqual(len(stock_request.move_ids), 0)
        self.assertEqual(stock_request.qty_in_progress, 0.0)

        purchase = stock_request.sudo().purchase_ids[0]
        purchase.button_confirm()
        picking = purchase.picking_ids[0]
        picking.action_confirm()

        self.assertEqual(stock_request.qty_in_progress, 5.0)
        self.assertEqual(stock_request.qty_done, 0.0)

        picking.action_assign()
        packout1 = picking.move_line_ids[0]
        packout1.qty_done = 5
        picking.action_done()

        self.assertEqual(stock_request.qty_in_progress, 0.0)
        self.assertEqual(stock_request.qty_done,
                         stock_request.product_uom_qty)
        self.assertEqual(stock_request.state, 'done')

    def test_create_request_02(self):
        """Multiple Stock requests with buy rule"""
        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 5.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }

        stock_request_1 = self.stock_request.sudo(
            self.stock_request_user).create(vals)
        stock_request_2 = self.stock_request.sudo(
            self.stock_request_manager).create(vals)

        stock_request_1.action_confirm()
        self.assertEqual(sum(stock_request_1.sudo().purchase_line_ids.mapped(
            'product_qty')), 5)

        stock_request_2.action_confirm()

        self.assertEqual(sum(stock_request_2.sudo().purchase_line_ids.mapped(
            'product_qty')), 10)

        stock_request_1.refresh()
        stock_request_2.refresh()

        self.assertEqual(len(stock_request_1.sudo().purchase_ids), 1)
        self.assertEqual(len(stock_request_2.sudo().purchase_ids), 1)
        self.assertEqual(len(stock_request_1.sudo().purchase_ids), 1)
        self.assertEqual(len(stock_request_2.sudo().purchase_line_ids), 1)
        self.assertEqual(stock_request_1.sudo().purchase_ids,
                         stock_request_2.sudo().purchase_ids)
        self.assertEqual(stock_request_1.sudo().purchase_line_ids,
                         stock_request_2.sudo().purchase_line_ids)

        purchase = stock_request_1.sudo().purchase_ids[0]

        purchase.button_confirm()
        picking = purchase.picking_ids[0]
        picking.action_confirm()

        self.assertEqual(stock_request_1.qty_in_progress, 5.0)
        self.assertEqual(stock_request_1.qty_done, 0.0)
        self.assertEqual(stock_request_2.qty_in_progress, 5.0)
        self.assertEqual(stock_request_2.qty_done, 0.0)

        picking.action_assign()
        packout1 = picking.move_line_ids[0]
        packout1.qty_done = 10
        picking.action_done()

        self.assertEqual(stock_request_1.qty_in_progress, 0.0)
        self.assertEqual(stock_request_1.qty_done,
                         stock_request_1.product_uom_qty)

        self.assertEqual(stock_request_2.qty_in_progress, 0.0)
        self.assertEqual(stock_request_2.qty_done,
                         stock_request_2.product_uom_qty)

    def test_view_actions(self):
        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 5.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }

        stock_request = self.stock_request.sudo().create(vals)
        stock_request.action_confirm()

        action = stock_request.action_view_purchase()

        self.assertEqual(action['domain'], '[]')
        self.assertEqual('views' in action.keys(), True)
        self.assertEqual(action['res_id'],
                         stock_request.purchase_ids[0].id)

        action = stock_request.purchase_ids[0].action_view_stock_request()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_id'], stock_request.id)
