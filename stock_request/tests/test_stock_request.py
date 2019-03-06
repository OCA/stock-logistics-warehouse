# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common
from odoo import fields, exceptions
from odoo.tools.misc import mute_logger
from collections import Counter


class TestStockRequest(common.TransactionCase):
    def setUp(self):
        super(TestStockRequest, self).setUp()

        # common models
        self.stock_request = self.env['stock.request']
        self.request_order = self.env['stock.request.order']

        # refs
        self.stock_request_user_group = \
            self.env.ref('stock_request.group_stock_request_user')
        self.stock_request_manager_group = \
            self.env.ref('stock_request.group_stock_request_manager')
        self.main_company = self.env.ref('base.main_company')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.categ_unit = self.env.ref('product.product_uom_categ_unit')
        self.virtual_loc = self.env.ref('stock.stock_location_customers')

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
        self.product_company_2 = self._create_product('SH_2', 'Shoes',
                                                      self.company_2.id)

        self.ressuply_loc = self.env['stock.location'].create({
            'name': 'Ressuply',
            'location_id': self.warehouse.view_location_id.id,
        })

        self.ressuply_loc_2 = self.env['stock.location'].create({
            'name': 'Ressuply',
            'location_id': self.wh2.view_location_id.id,
        })

        self.route = self.env['stock.location.route'].create({
            'name': 'Transfer',
            'product_categ_selectable': False,
            'product_selectable': True,
            'company_id': self.main_company.id,
            'sequence': 10,
        })

        self.route_2 = self.env['stock.location.route'].create({
            'name': 'Transfer',
            'product_categ_selectable': False,
            'product_selectable': True,
            'company_id': self.company_2.id,
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

        self.env['procurement.rule'].create({
            'name': 'Transfer',
            'route_id': self.route_2.id,
            'location_src_id': self.ressuply_loc_2.id,
            'location_id': self.wh2.lot_stock_id.id,
            'action': 'move',
            'picking_type_id': self.wh2.int_type_id.id,
            'procure_method': 'make_to_stock',
            'warehouse_id': self.wh2.id,
            'company_id': self.company_2.id,
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

    def _create_product(self, default_code, name, company_id, **vals):
        return self.env['product.product'].create(dict(
            name=name,
            default_code=default_code,
            uom_id=self.env.ref('product.product_uom_unit').id,
            company_id=company_id,
            type='product',
            **vals
        ))

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

    def test_defaults_order(self):
        vals = {}
        order = self.request_order.sudo(
            self.stock_request_user.id).with_context(
            company_id=self.main_company.id).create(vals)

        self.assertEqual(
            order.requested_by, self.stock_request_user)

        self.assertEqual(
            order.warehouse_id, self.warehouse)

        self.assertEqual(
            order.location_id, self.warehouse.lot_stock_id)

    def test_onchanges_order(self):
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
            })]
        }
        order = self.request_order.sudo(
            self.stock_request_user).new(vals)
        self.stock_request_user.company_id = self.company_2
        order.company_id = self.company_2

        order.onchange_company_id()

        stock_request = order.stock_request_ids
        self.assertEqual(order.warehouse_id, self.wh2)
        self.assertEqual(order.location_id, self.wh2.lot_stock_id)
        self.assertEqual(order.warehouse_id, stock_request.warehouse_id)

        procurement_group = self.env['procurement.group'].create({
            'name': 'TEST'
        })
        order.procurement_group_id = procurement_group
        order.onchange_procurement_group_id()
        self.assertEqual(
            order.procurement_group_id,
            order.stock_request_ids.procurement_group_id)

        order.procurement_group_id = procurement_group
        order.onchange_procurement_group_id()
        self.assertEqual(
            order.procurement_group_id,
            order.stock_request_ids.procurement_group_id)
        order.picking_policy = 'one'

        order.onchange_picking_policy()
        self.assertEqual(
            order.picking_policy,
            order.stock_request_ids.picking_policy)

        order.expected_date = fields.Date.today()
        order.onchange_expected_date()
        self.assertEqual(
            order.expected_date,
            order.stock_request_ids.expected_date)

        order.requested_by = self.stock_request_manager
        order.onchange_requested_by()
        self.assertEqual(
            order.requested_by,
            order.stock_request_ids.requested_by)

    def test_onchanges(self):
        self.product.route_ids = [(6, 0, self.route.ids)]
        vals = {
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 5.0,
            'company_id': self.main_company.id,
        }
        stock_request = self.stock_request.sudo(
            self.stock_request_user).new(vals)
        stock_request.product_id = self.product
        vals = stock_request.default_get(['warehouse_id', 'company_id'])
        stock_request.update(vals)
        stock_request.onchange_product_id()
        self.assertIn(self.route.id, stock_request.route_ids.ids)

        self.stock_request_user.company_id = self.company_2
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
            company_id=self.company_2.id
        ).create({
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

    def test_stock_request_order_validations_01(self):
        """ Testing the discrepancy in warehouse_id between
        stock request and order"""
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.wh2.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.sudo(
                self.stock_request_user).create(vals)

    def test_stock_request_order_validations_02(self):
        """ Testing the discrepancy in location_id between
        stock request and order"""
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.wh2.lot_stock_id.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.sudo(
                self.stock_request_user).create(vals)

    def test_stock_request_order_validations_03(self):
        """ Testing the discrepancy in requested_by between
        stock request and order"""
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'requested_by': self.stock_request_user.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'requested_by': self.stock_request_manager.id,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.sudo(
                self.stock_request_user).create(vals)

    def test_stock_request_order_validations_04(self):
        """ Testing the discrepancy in procurement_group_id between
        stock request and order"""
        procurement_group = self.env['procurement.group'].create({
            'name': 'Procurement',
        })
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'procurement_group_id': procurement_group.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.sudo(
                self.stock_request_user).create(vals)

    @mute_logger('odoo.models')
    def test_stock_request_order_validations_05(self):
        """ Testing the discrepancy in company between
        stock request and order"""
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.company_2.id,
            'warehouse_id': self.wh2.id,
            'location_id': self.wh2.lot_stock_id.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.sudo(
                self.stock_request_user).create(vals)

    def test_stock_request_order_validations_06(self):
        """ Testing the discrepancy in expected dates between
        stock request and order"""
        expected_date = fields.Date.today()
        child_expected_date = '2015-01-01'
        vals = {
            'company_id': self.company_2.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': child_expected_date,
            })]
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.sudo().create(vals)

    def test_stock_request_order_validations_07(self):
        """ Testing the discrepancy in picking policy between
        stock request and order"""
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'picking_policy': 'one',
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.sudo(
                self.stock_request_user).create(vals)

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
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }

        order = self.request_order.sudo(
            self.stock_request_user).create(vals)

        stock_request = order.stock_request_ids

        self.product.route_ids = [(6, 0, self.route.ids)]
        order.action_confirm()
        self.assertEqual(order.state, 'open')
        self.assertEqual(stock_request.state, 'open')

        self.assertEqual(len(order.sudo().picking_ids), 1)
        self.assertEqual(len(order.sudo().move_ids), 1)
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
        self.assertEqual(order.state, 'done')
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
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }

        order = self.request_order.sudo(
            self.stock_request_user).create(vals)

        self.product.route_ids = [(6, 0, self.route.ids)]
        order.action_confirm()
        stock_request = order.stock_request_ids
        self.assertEqual(len(order.sudo().picking_ids), 1)
        self.assertEqual(len(order.sudo().move_ids), 1)
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
        order.action_cancel()

        self.assertEqual(stock_request.qty_in_progress, 0.0)
        self.assertEqual(stock_request.qty_done, 0.0)
        self.assertEqual(len(stock_request.sudo().picking_ids), 0)

        # Set the request back to draft
        order.action_draft()
        self.assertEqual(order.state, 'draft')
        self.assertEqual(stock_request.state, 'draft')

        # Re-confirm. We expect new pickings to be created
        order.action_confirm()
        self.assertEqual(len(stock_request.sudo().picking_ids), 1)
        self.assertEqual(len(stock_request.sudo().move_ids), 2)

    def test_view_actions(self):
        expected_date = fields.Date.today()
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }

        order = self.request_order.sudo().create(vals)
        self.product.route_ids = [(6, 0, self.route.ids)]

        order.action_confirm()
        stock_request = order.stock_request_ids
        self.assertTrue(stock_request.picking_ids)
        self.assertTrue(order.picking_ids)

        action = order.action_view_transfer()
        self.assertEqual('domain' in action.keys(), True)
        self.assertEqual('views' in action.keys(), True)
        self.assertEqual(action['res_id'], order.picking_ids[0].id)

        action = order.action_view_stock_requests()
        self.assertEqual('domain' in action.keys(), True)
        self.assertEqual('views' in action.keys(), True)
        self.assertEqual(action['res_id'], stock_request[0].id)

        action = stock_request.action_view_transfer()
        self.assertEqual('domain' in action.keys(), True)
        self.assertEqual('views' in action.keys(), True)
        self.assertEqual(action['res_id'], stock_request.picking_ids[0].id)

        action = stock_request.picking_ids[0].action_view_stock_request()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_id'], stock_request.id)

    @mute_logger('odoo.models')
    def test_stock_request_constrains(self):
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

        # Cannot assign a warehouse that belongs to another company
        with self.assertRaises(exceptions.ValidationError):
            stock_request.warehouse_id = self.wh2
        # Cannot assign a product that belongs to another company
        with self.assertRaises(exceptions.ValidationError):
            stock_request.product_id = self.product_company_2
        # Cannot assign a location that belongs to another company
        with self.assertRaises(exceptions.ValidationError):
            stock_request.location_id = self.wh2.lot_stock_id
        # Cannot assign a route that belongs to another company
        with self.assertRaises(exceptions.ValidationError):
            stock_request.route_id = self.route_2

    def test_stock_request_order_from_products(self):
        product_A1 = self._create_product('CODEA1', 'Product A1',
                                          self.main_company.id)
        template_A = product_A1.product_tmpl_id
        product_A2 = self._create_product(
            'CODEA2', 'Product A2', self.main_company.id,
            product_tmpl_id=template_A.id)
        product_A3 = self._create_product(
            'CODEA3', 'Product A3', self.main_company.id,
            product_tmpl_id=template_A.id)
        product_B1 = self._create_product('CODEB1', 'Product B1',
                                          self.main_company.id)
        template_B = product_B1.product_tmpl_id
        # One archived variant of B
        self._create_product(
            'CODEB2', 'Product B2', self.main_company.id,
            product_tmpl_id=template_B.id, active=False)
        Order = self.request_order

        # Selecting some variants and creating an order
        preexisting = Order.search([])
        wanted_products = product_A1 + product_A2 + product_B1
        action = Order._create_from_product_multiselect(wanted_products)
        new_order = Order.search([]) - preexisting
        self.assertEqual(len(new_order), 1)
        self.assertEqual(action['res_id'], new_order.id,
                         msg="Returned action references the wrong record")
        self.assertEqual(
            Counter(wanted_products),
            Counter(new_order.stock_request_ids.mapped('product_id')),
            msg="Not all wanted products were ordered"
        )

        # Selecting a template and creating an order
        preexisting = Order.search([])
        action = Order._create_from_product_multiselect(template_A)
        new_order = Order.search([]) - preexisting
        self.assertEqual(len(new_order), 1)
        self.assertEqual(action['res_id'], new_order.id,
                         msg="Returned action references the wrong record")
        self.assertEqual(
            Counter(product_A1 + product_A2 + product_A3),
            Counter(new_order.stock_request_ids.mapped('product_id')),
            msg="Not all of the template's variants were ordered"
        )

        # Selecting a template
        preexisting = Order.search([])
        action = Order._create_from_product_multiselect(
            template_A + template_B)
        new_order = Order.search([]) - preexisting
        self.assertEqual(len(new_order), 1)
        self.assertEqual(action['res_id'], new_order.id,
                         msg="Returned action references the wrong record")
        self.assertEqual(
            Counter(product_A1 + product_A2 + product_A3 + product_B1),
            Counter(new_order.stock_request_ids.mapped('product_id')),
            msg="Inactive variant was ordered though it shouldn't have been"
        )

        # If a user does not have stock request rights, they can still trigger
        # the action from the products, so test that they get a friendlier
        # error message.
        self.stock_request_user.groups_id -= self.stock_request_user_group
        with self.assertRaisesRegexp(
                exceptions.UserError,
                "Unfortunately it seems you do not have the necessary rights "
                "for creating stock requests. Please contact your "
                "administrator."):
            Order.sudo(
                self.stock_request_user
            )._create_from_product_multiselect(template_A + template_B)

        # Empty recordsets should just return False
        self.assertFalse(Order._create_from_product_multiselect(
            self.env['product.product']))

        # Wrong model should just raise ValidationError
        with self.assertRaises(exceptions.ValidationError):
            Order._create_from_product_multiselect(self.stock_request_user)

    def test_allow_virtual_location(self):
        self.main_company.stock_request_allow_virtual_loc = True
        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 5.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.virtual_loc.id,
        }
        stock_request = self.stock_request.sudo(
            self.stock_request_user).create(vals)
        stock_request.onchange_allow_virtual_location()
        self.assertTrue(stock_request.allow_virtual_location)
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.virtual_loc.id,
        }
        order = self.request_order.sudo(
            self.stock_request_user).create(vals)
        order.onchange_allow_virtual_location()
        self.assertTrue(order.allow_virtual_location)

    def test_onchange_wh_no_effect_from_order(self):
        vals = {
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.virtual_loc.id,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.virtual_loc.id,
            })]
        }
        order = self.request_order.sudo(
            self.stock_request_user).create(vals)
        order.stock_request_ids.onchange_warehouse_id()
        self.assertEqual(
            order.stock_request_ids[0].location_id, self.virtual_loc)
