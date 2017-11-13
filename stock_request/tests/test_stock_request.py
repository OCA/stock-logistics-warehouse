# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common
from odoo import exceptions


class TestStockRequest(common.TransactionCase):

    def setUp(self):
        super(TestStockRequest, self).setUp()

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
        self.product = self._create_product('SH', 'Shoes', False)

        self.ressuply_loc = self.env['stock.location'].create({
            'name': 'Ressuply',
            'location_id': self.warehouse.view_location_id.id,
        })

        self.route = self.env['stock.location.route'].create({
            'name': 'Transfer',
            'product_categ_selectable': False,
            'product_selectable': True,
            'company_id': self.main_company.id,
            'sequence': 10,
        })

        self.uom_dozen = self.env['product.uom'].create({
            'name': 'Test-DozenA',
            'category_id': self.categ_unit.id,
            'factor_inv': 12,
            'uom_type': 'bigger',
            'rounding': 0.001})

        self.env['procurement.rule'].create({
            'name': 'Transfer',
            'route_id': self.route.id,
            'location_src_id': self.ressuply_loc.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'action': 'move',
            'picking_type_id': self.warehouse.int_type_id.id,
            'procure_method': 'make_to_stock',
            'warehouse_id': self.warehouse.id,
            'company_id': self.main_company.id,
            'propagate': 'False',
        })

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
        })

    def test_defaults(self):

        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 5.0,
        }
        stock_request = self.stock_request.sudo(
            self.stock_request_user.id).with_context(
            company_id=self.main_company.id).create(vals)

        self.assertEqual(
            stock_request.requested_by, self.stock_request_user)

        self.assertEqual(
            stock_request.warehouse_id, self.warehouse)

        self.assertEqual(
            stock_request.location_id, self.warehouse.lot_stock_id)

    def test_onchanges(self):
        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 5.0,
            'company_id': self.main_company.id,
        }
        stock_request = self.stock_request.sudo(
            self.stock_request_user).new(vals)
        self.stock_request_user.company_id = self.company_2
        stock_request.default_get(['warehouse_id', 'company_id'])
        stock_request.company_id = self.company_2
        stock_request.onchange_company_id()

        self.assertEqual(
            stock_request.warehouse_id, self.wh2)
        self.assertEqual(
            stock_request.location_id, self.wh2.lot_stock_id)

        product = self.env['product.product'].create({
            'name': 'Wheat',
            'uom_id': self.env.ref('product.product_uom_kgm').id,
            'uom_po_id': self.env.ref('product.product_uom_kgm').id,
        })

        # Test onchange_product_id
        stock_request.product_id = product
        res = stock_request.onchange_product_id()

        self.assertEqual(res['domain']['product_uom_id'],
                         [('category_id', '=',
                           product.uom_id.category_id.id)])
        self.assertEqual(
            stock_request.product_uom_id,
            self.env.ref('product.product_uom_kgm'))

        stock_request.product_id = self.env['product.product']
        res = stock_request.onchange_product_id()

        self.assertEqual(res['domain']['product_uom_id'], [])

        # Test onchange_warehouse_id
        wh2_2 = self.env['stock.warehouse'].with_context(
            company_id=self.company_2.id).create({
                'name': 'C2_2',
                'code': 'C2_2',
                'company_id': self.company_2.id
            })
        stock_request.warehouse_id = wh2_2
        stock_request.onchange_warehouse_id()

        self.assertEqual(stock_request.warehouse_id, wh2_2)

        self.stock_request_user.company_id = self.main_company
        stock_request.warehouse_id = self.warehouse
        stock_request.onchange_warehouse_id()

        self.assertEqual(
            stock_request.company_id, self.main_company)
        self.assertEqual(
            stock_request.location_id, self.warehouse.lot_stock_id)

    def test_stock_request_validations_01(self):
        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.env.ref('product.product_uom_kgm').id,
            'product_uom_qty': 5.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }
        # Select a UoM that is incompatible with the product's UoM
        with self.assertRaises(exceptions.ValidationError):
            self.stock_request.sudo(
                self.stock_request_user).create(vals)

    def test_stock_request_validations_02(self):
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

        # With no route found, should raise an error
        with self.assertRaises(exceptions.UserError):
            stock_request.action_confirm()

    def test_create_request_01(self):

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

        self.product.route_ids = [(6, 0, self.route.ids)]
        stock_request.action_confirm()
        self.assertEqual(stock_request.state, 'open')
        self.assertEqual(len(stock_request.sudo().picking_ids), 1)
        self.assertEqual(len(stock_request.sudo().move_ids), 1)
        self.assertEqual(stock_request.sudo().move_ids[0].location_dest_id,
                         stock_request.location_id)
        self.assertEqual(stock_request.qty_in_progress,
                         stock_request.product_uom_qty)
        self.env['stock.quant'].create({
            'product_id': self.product.id,
            'location_id': self.ressuply_loc.id,
            'quantity': 5.0})
        picking = stock_request.sudo().picking_ids[0]
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
        """Use different UoM's"""

        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.uom_dozen.id,
            'product_uom_qty': 1.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }

        stock_request = self.stock_request.sudo(
            self.stock_request_user).create(vals)

        self.product.route_ids = [(6, 0, self.route.ids)]
        stock_request.action_confirm()
        self.assertEqual(stock_request.state, 'open')
        self.assertEqual(len(stock_request.sudo().picking_ids), 1)
        self.assertEqual(len(stock_request.sudo().move_ids), 1)
        self.assertEqual(stock_request.sudo().move_ids[0].location_dest_id,
                         stock_request.location_id)
        self.assertEqual(stock_request.qty_in_progress,
                         stock_request.product_uom_qty)
        self.env['stock.quant'].create({
            'product_id': self.product.id,
            'location_id': self.ressuply_loc.id,
            'quantity': 12.0})
        picking = stock_request.sudo().picking_ids[0]
        picking.action_confirm()
        self.assertEqual(stock_request.qty_in_progress, 1.0)
        self.assertEqual(stock_request.qty_done, 0.0)
        picking.action_assign()
        packout1 = picking.move_line_ids[0]
        packout1.qty_done = 1
        picking.action_done()
        self.assertEqual(stock_request.qty_in_progress, 0.0)
        self.assertEqual(stock_request.qty_done,
                         stock_request.product_uom_qty)
        self.assertEqual(stock_request.state, 'done')

    def test_create_request_03(self):
        """Multiple stock requests"""
        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 4.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }

        stock_request_1 = self.env['stock.request'].sudo(
            self.stock_request_user).create(vals)
        stock_request_2 = self.env['stock.request'].sudo(
            self.stock_request_manager).create(vals)
        stock_request_2.product_uom_qty = 6.0
        self.product.route_ids = [(6, 0, self.route.ids)]
        stock_request_1.action_confirm()
        stock_request_2.action_confirm()
        self.assertEqual(len(stock_request_1.sudo().picking_ids), 1)
        self.assertEqual(stock_request_1.sudo().picking_ids,
                         stock_request_2.sudo().picking_ids)
        self.assertEqual(stock_request_1.sudo().move_ids,
                         stock_request_2.sudo().move_ids)
        self.env['stock.quant'].create({
            'product_id': self.product.id,
            'location_id': self.ressuply_loc.id,
            'quantity': 10.0})
        picking = stock_request_1.sudo().picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        packout1 = picking.move_line_ids[0]
        packout1.qty_done = 10
        picking.action_done()

    def test_cancel_request(self):
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

        self.product.route_ids = [(6, 0, self.route.ids)]
        stock_request.action_confirm()
        self.assertEqual(len(stock_request.sudo().picking_ids), 1)
        self.assertEqual(len(stock_request.sudo().move_ids), 1)
        self.assertEqual(stock_request.sudo().move_ids[0].location_dest_id,
                         stock_request.location_id)
        self.assertEqual(stock_request.qty_in_progress,
                         stock_request.product_uom_qty)
        self.env['stock.quant'].create({
            'product_id': self.product.id,
            'location_id': self.ressuply_loc.id,
            'quantity': 5.0})
        picking = stock_request.sudo().picking_ids[0]
        picking.action_confirm()
        self.assertEqual(stock_request.qty_in_progress, 5.0)
        self.assertEqual(stock_request.qty_done, 0.0)
        picking.action_assign()
        stock_request.action_cancel()

        self.assertEqual(stock_request.qty_in_progress, 0.0)
        self.assertEqual(stock_request.qty_done, 0.0)
        self.assertEqual(len(stock_request.sudo().picking_ids), 0)

        # Set the request back to draft
        stock_request.action_draft()

        self.assertEqual(stock_request.state, 'draft')

        # Re-confirm. We expect new pickings to be created
        stock_request.action_confirm()
        self.assertEqual(len(stock_request.sudo().picking_ids), 1)
        self.assertEqual(len(stock_request.sudo().move_ids), 2)

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
        self.product.route_ids = [(6, 0, self.route.ids)]
        stock_request.action_confirm()
        action = stock_request.action_view_transfer()

        self.assertEqual('domain' in action.keys(), True)
        self.assertEqual('views' in action.keys(), True)
        self.assertEqual(action['res_id'], stock_request.picking_ids[0].id)

        action = stock_request.picking_ids[0].action_view_stock_request()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_id'], stock_request.id)
