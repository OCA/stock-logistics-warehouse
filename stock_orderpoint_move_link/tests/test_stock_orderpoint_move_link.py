# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast
from odoo.tests.common import SavepointCase


class TestStockOrderpointMoveLink(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.stock_move = cls.env['stock.move']
        cls.stock_picking = cls.env['stock.picking']
        cls.product_model = cls.env['product.product']
        cls.orderpoint_model = cls.env['stock.warehouse.orderpoint']
        cls.loc_model = cls.env['stock.location']
        cls.route_model = cls.env['stock.location.route']
        cls.group_obj = cls.env['procurement.group']

        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.stock_loc = cls.env.ref('stock.stock_location_stock')

        # Create a new location and route:
        cls.test_location_01 = cls.loc_model.create({
            'name': 'Test location 01',
            'usage': 'internal',
            'location_id': cls.warehouse.view_location_id.id,
        })
        cls.test_route_01 = cls.route_model.create({
            'name': 'Stock -> Test_1',
            'product_selectable': True,
            'pull_ids': [(0, 0, {
                'name': 'stock to test',
                'action': 'move',
                'location_id': cls.test_location_01.id,
                'location_src_id': cls.stock_loc.id,
                'procure_method': 'make_to_stock',
                'picking_type_id': cls.env.ref(
                    'stock.picking_type_internal').id,
                'propagate': True
            })]
        })

        # Create a new location and route:
        cls.test_location_02 = cls.loc_model.create({
            'name': 'Test location 02',
            'usage': 'internal',
            'location_id': cls.warehouse.view_location_id.id,
        })
        cls.test_route_02 = cls.route_model.create({
            'name': 'Stock -> Test',
            'product_selectable': True,
            'pull_ids': [(0, 0, {
                'name': 'Test_1 -> Test_2',
                'action': 'move',
                'location_id': cls.test_location_02.id,
                'location_src_id': cls.test_location_01.id,
                'procure_method': 'make_to_order',
                'picking_type_id': cls.env.ref(
                    'stock.picking_type_internal').id,
                'propagate': True
            })]
        })

        # Prepare Products:
        routes = cls.test_route_01 + cls.test_route_02
        cls.product = cls.product_model.create({
            'name': 'Test Product',
            'route_ids': [(6, 0, routes.ids)],
        })

        cls.orderpoint_test_02_loc = cls.orderpoint_model.create({
            'warehouse_id': cls.warehouse.id,
            'location_id': cls.test_location_02.id,
            'product_id': cls.product.id,
            'product_min_qty': 10.0,
            'product_max_qty': 20.0,
            'product_uom': cls.product.uom_id.id,
        })

        cls.group_obj.run_scheduler()

    def test_01_stock_orderpoint_move_link_indirect_routing(self):
        """Tests manual procurement fills requested_by field.
        Indirect Stock move creation (transfer -> transfer)."""
        sm = self.stock_move.search([
            ('location_dest_id', '=', self.test_location_01.id)])
        self.assertTrue(sm)
        self.assertEqual(sm.orderpoint_ids[0], self.orderpoint_test_02_loc)
        self.assertEqual(sm.origin, '%s, %s' % (
            self.test_route_02.pull_ids[0].name, sm.orderpoint_ids[0].name))

    def test_02_stock_orderpoint_move_link_action_view(self):
        sp_orderpoint = self.stock_move.search(
            [('orderpoint_ids', 'in', self.orderpoint_test_02_loc.id)]).mapped(
            'picking_id')
        result = self.orderpoint_test_02_loc.action_view_stock_picking()
        sp_action = self.stock_picking.search(
            ast.literal_eval(result['domain']))
        self.assertEquals(sp_orderpoint, sp_action)
