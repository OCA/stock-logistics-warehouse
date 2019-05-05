# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import TransactionCase
from datetime import datetime


class TestMtoMtsRoute(TransactionCase):

    def _procurement_create(self):
        self.procurement = self.env['procurement.order'].create({
            'location_id': self.env.ref('stock.stock_location_customers').id,
            'product_id': self.product.id,
            'product_qty': 2.0,
            'product_uom': 1,
            'warehouse_id': self.warehouse.id,
            'priority': '1',
            'date_planned': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': self.product.name,
            'origin': 'test',
            'group_id': self.group.id,
        })

    def test_standard_mto_route(self):
        mto_route = self.env.ref('stock.route_warehouse0_mto')
        self.product.route_ids = [(6, 0, [mto_route.id])]
        self._procurement_create()
        self.assertEqual(self.warehouse.mto_pull_id,
                         self.procurement.rule_id)
        self.assertEqual('make_to_order',
                         self.procurement.move_ids[0].procure_method)
        self.assertEqual(self.procurement.product_qty,
                         self.procurement.move_ids[0].product_uom_qty)
        self.assertEqual('waiting',
                         self.procurement.move_ids[0].state)

    def test_standard_mts_route(self):
        self._procurement_create()
        procurement_id = self.procurement_obj.search([
            ('group_id', '=', self.procurement.group_id.id),
            ('move_ids', '!=', False)], limit=1)
        self.assertEqual('make_to_stock',
                         procurement_id.move_ids[0].procure_method)
        self.assertEqual(self.procurement.product_qty,
                         procurement_id.move_ids[0].product_uom_qty)
        self.assertEqual('confirmed',
                         procurement_id.move_ids[0].state)

    def test_mts_mto_route_split(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        self.product.route_ids = [(6, 0, [mto_mts_route.id])]
        self.quant.qty = 1.0
        self._procurement_create()
        moves = self.env['stock.move'].search(
            [('group_id', '=', self.group.id)])
        self.assertEqual(2, len(moves))
        self.assertEqual(1.0, moves[0].product_uom_qty)

    def test_mts_mto_route_split_done(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        self.product.route_ids = [(6, 0, [mto_mts_route.id])]
        self.quant.qty = 1.0
        self._procurement_create()
        self.assertEqual(self.procurement.state, 'running')
        self.procurement.mts_mto_procurement_ids.mapped(
            'move_ids').action_done()
        self.assertEqual(self.procurement.state, 'done')

    def test_mts_mto_route_split_cancel(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        self.product.route_ids = [(6, 0, [mto_mts_route.id])]
        self.quant.qty = 1.0
        self._procurement_create()
        self.procurement.mts_mto_procurement_ids.cancel()
        self.assertEqual(self.procurement.state, 'running')
        self.procurement.check()
        self.assertEqual(self.procurement.state, 'cancel')

    def test_mts_mto_route_mts_only(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        self.product.route_ids = [(6, 0, [mto_mts_route.id])]
        self.quant.qty = 0.0
        self._procurement_create()
        moves = self.env['stock.move'].search(
            [('group_id', '=', self.group.id)])
        self.assertEqual(1, len(moves))
        self.assertEqual(2.0, moves[0].product_uom_qty)
        self.assertEqual('make_to_order',
                         moves[0].procure_method)

    def test_mts_mto_route_mto_only(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        self.product.route_ids = [(6, 0, [mto_mts_route.id])]
        self.quant.qty = 3.0
        self._procurement_create()
        moves = self.env['stock.move'].search(
            [('group_id', '=', self.group.id)])
        self.assertEqual(1, len(moves))
        self.assertEqual(2.0, moves[0].product_uom_qty)
        self.assertEqual('make_to_stock',
                         moves[0].procure_method)

    def test_mts_mto_route_mto_removed(self):
        self.env.ref('stock_mts_mto_rule.route_mto_mts').unlink()
        self.warehouse.mts_mto_rule_id = False
        with self.assertRaises(exceptions.Warning):
            self.warehouse.mto_mts_management = True

    def test_mts_mto_route_mts_removed(self):
        self.warehouse.mto_mts_management = True
        self.env['procurement.rule'].search([
            ('location_src_id', '=', self.warehouse.lot_stock_id.id),
            ('route_id', '=', self.warehouse.delivery_route_id.id),
        ]).unlink()
        self.warehouse.mts_mto_rule_id = False
        with self.assertRaises(exceptions.Warning):
            self.warehouse.mto_mts_management = True

    def test_mts_mto_route_mto_no_mts_rule(self):
        self.warehouse.mts_mto_rule_id = False
        self.warehouse.mto_pull_id = False
        with self.assertRaises(exceptions.Warning):
            self.warehouse.mto_mts_management = True

    def test_create_routes(self):
        rule_obj = self.env['procurement.rule']
        created_routes = self.warehouse.create_routes()
        mts_mto_route = rule_obj.browse(created_routes['mts_mto_rule_id'])
        self.assertEqual(mts_mto_route.warehouse_id, self.warehouse)
        self.assertEqual(
            mts_mto_route.location_id, self.warehouse.mto_pull_id.location_id)
        self.assertEqual(
            mts_mto_route.picking_type_id,
            self.warehouse.mto_pull_id.picking_type_id)
        self.assertEqual(
            mts_mto_route.route_id,
            self.env.ref('stock_mts_mto_rule.route_mto_mts'))

    def test_remove_mts_mto_management(self):
        warehouse_rule = self.warehouse.mts_mto_rule_id
        self.assertTrue(self.warehouse.mts_mto_rule_id)
        self.warehouse.mto_mts_management = False
        self.assertFalse(warehouse_rule.exists())
        self.assertFalse(self.warehouse.mts_mto_rule_id)

    def test_get_all_routes_for_wh(self):
        routes = self.warehouse.get_all_routes_for_wh()
        self.assertTrue(self.warehouse.mts_mto_rule_id)
        self.assertTrue(self.warehouse.mts_mto_rule_id.route_id in routes)

    def test_rename_warehouse(self):
        rule_name = self.warehouse.mts_mto_rule_id.name
        new_warehouse_name = 'NewName'
        new_rule_name = rule_name.replace(
            self.warehouse.name, new_warehouse_name, 1)
        self.warehouse.name = new_warehouse_name
        self.assertEqual(new_rule_name, self.warehouse.mts_mto_rule_id.name)

    def setUp(self):
        super(TestMtoMtsRoute, self).setUp()
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse.mto_mts_management = True
        self.product = self.env.ref('product.product_product_4')
        self.company_partner = self.env.ref('base.main_partner')
        self.procurement_obj = self.env['procurement.order']
        self.group = self.env['procurement.group'].create({
            'name': 'test',
        })

        self.quant = self.env['stock.quant'].create({
            'owner_id': self.company_partner.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
            'qty': 0.0,
        })
