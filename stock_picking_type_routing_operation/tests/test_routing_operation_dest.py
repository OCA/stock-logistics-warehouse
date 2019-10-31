# Copyright 2019 Camptocamp (https://www.camptocamp.com)

from odoo.tests import common


class TestDestRoutingOperation(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_delta = cls.env.ref('base.res_partner_4')
        cls.wh = cls.env['stock.warehouse'].create({
            'name': 'Base Warehouse',
            'reception_steps': 'one_step',
            'delivery_steps': 'pick_ship',
            'code': 'WHTEST',
        })

        cls.supplier_loc = cls.env.ref('stock.stock_location_suppliers')
        cls.location_hb = cls.env['stock.location'].create({
            'name': 'Highbay',
            'location_id': cls.wh.lot_stock_id.id,
        })
        cls.location_shelf_1 = cls.env['stock.location'].create({
            'name': 'Shelf 1',
            'location_id': cls.wh.lot_stock_id.id,
        })
        cls.location_hb_1 = cls.env['stock.location'].create({
            'name': 'Highbay Shelf 1',
            'location_id': cls.location_hb.id,
        })
        cls.location_hb_1_1 = cls.env['stock.location'].create({
            'name': 'Highbay Shelf 1 Bin 1',
            'location_id': cls.location_hb_1.id,
        })
        cls.location_hb_1_2 = cls.env['stock.location'].create({
            'name': 'Highbay Shelf 1 Bin 2',
            'location_id': cls.location_hb_1.id,
        })

        cls.location_handover = cls.env['stock.location'].create({
            'name': 'Handover',
            'location_id': cls.wh.lot_stock_id.id,
        })

        cls.product1 = cls.env['product.product'].create({
            'name': 'Product 1', 'type': 'product',
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'Product 2', 'type': 'product',
        })

        picking_type_sequence = cls.env['ir.sequence'].create({
            'name': 'WH/Handover',
            'prefix': 'WH/HO/',
            'padding': 5,
            'company_id': cls.wh.company_id.id,
        })
        cls.pick_type_routing_op = cls.env['stock.picking.type'].create({
            'name': 'Routing operation',
            'code': 'internal',
            'use_create_lots': False,
            'use_existing_lots': True,
            'default_location_src_id': cls.location_handover.id,
            'default_location_dest_id': cls.location_hb.id,
            'sequence_id': picking_type_sequence.id,
        })
        cls.location_hb.write({
            'dest_routing_picking_type_id': cls.pick_type_routing_op.id
        })

    def _create_supplier_input_highbay(self, wh, products=None):
        """Create pickings supplier->input, input-> highbay

        Products must be a list of tuples (product, quantity).
        One stock move will be create for each tuple.
        """
        if products is None:
            products = []
        in_picking = self.env['stock.picking'].create({
            'location_id': self.supplier_loc.id,
            'location_dest_id': wh.wh_input_stock_loc_id.id,
            'partner_id': self.partner_delta.id,
            'picking_type_id': wh.in_type_id.id,
        })

        internal_picking = self.env['stock.picking'].create({
            'location_id': wh.wh_input_stock_loc_id.id,
            'location_dest_id': self.location_hb_1_2.id,
            'partner_id': self.partner_delta.id,
            'picking_type_id': wh.int_type_id.id,
        })

        for product, qty in products:
            dest = self.env['stock.move'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': product.uom_id.id,
                'picking_id': internal_picking.id,
                'location_id': wh.wh_input_stock_loc_id.id,
                'location_dest_id': self.location_hb_1_2.id,
                'state': 'waiting',
                'procure_method': 'make_to_order',
            })

            self.env['stock.move'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': product.uom_id.id,
                'picking_id': in_picking.id,
                'location_id': self.supplier_loc.id,
                'location_dest_id': wh.wh_input_stock_loc_id.id,
                'move_dest_ids': [(4, dest.id)],
                'state': 'confirmed',
            })
        in_picking.action_assign()
        return in_picking, internal_picking

    def _update_product_qty_in_location(self, location, product, quantity):
        self.env['stock.quant']._update_available_quantity(
            product, location, quantity
        )

    def assert_src_input(self, record):
        self.assertEqual(record.location_id, self.wh.wh_input_stock_loc_id)

    def assert_dest_input(self, record):
        self.assertEqual(
            record.location_dest_id,
            self.wh.wh_input_stock_loc_id
        )

    def assert_src_handover(self, record):
        self.assertEqual(record.location_id, self.location_handover)

    def assert_dest_handover(self, record):
        self.assertEqual(record.location_dest_id, self.location_handover)

    def assert_src_shelf1(self, record):
        self.assertEqual(record.location_id, self.location_shelf_1)

    def assert_dest_shelf1(self, record):
        self.assertEqual(record.location_dest_id, self.location_shelf_1)

    def assert_src_highbay_1_2(self, record):
        self.assertEqual(record.location_id, self.location_hb_1_2)

    def assert_dest_highbay_1_2(self, record):
        self.assertEqual(record.location_dest_id, self.location_hb_1_2)

    def assert_src_supplier(self, record):
        self.assertEqual(record.location_id, self.supplier_loc)

    def process_operations(self, move):
        qty = move.move_line_ids.product_uom_qty
        move.move_line_ids.qty_done = qty
        move.picking_id.action_done()

    def test_change_location_to_routing_operation(self):
        in_picking, internal_picking = self._create_supplier_input_highbay(
            self.wh, [(self.product1, 10)]
        )
        move_a = in_picking.move_lines
        move_b = internal_picking.move_lines
        self.assertEqual(move_a.state, 'assigned')
        self.process_operations(move_a)

        # ml = move_b.move_line_ids
        # self.assertEqual(len(ml), 1)
        # self.assert_src_input(ml)
        # self.assert_dest_handover(ml)

        # self.assertEqual(
        #     ml.picking_id.picking_type_id, self.pick_type_routing_op
        # )

        self.assert_src_supplier(move_a)
        self.assert_dest_input(move_a)
        self.assert_src_handover(move_b)
        # the move stays B stays on the same dest location
        self.assert_dest_highbay_1_2(move_b)

        # we should have a move between move_a and move_b to make
        # the bridge from input to handover
        move_middle = move_a.move_dest_ids
        # the middle move stays in the same source location than the original
        # move: the move line will be in the sub-locations (handover)

        self.assert_src_input(move_middle)
        self.assert_dest_handover(move_middle)

        self.assertEquals(
            move_middle.picking_type_id,
            self.pick_type_routing_op
        )
        self.assertEquals(
            move_middle.picking_id.picking_type_id,
            self.pick_type_routing_op
        )
        self.assertEquals(
            move_a.picking_id.picking_type_id,
            self.wh.in_type_id
        )
        self.assertEquals(
            move_b.picking_id.picking_type_id,
            self.wh.int_type_id
        )
        self.assertEqual(move_a.state, 'done')
        self.assertEqual(move_middle.state, 'assigned')
        self.assertEqual(move_b.state, 'waiting')

        # we deliver middle to check that our last move line properly takes
        # goods from the handover
        self.process_operations(move_middle)

        self.assertEqual(move_a.state, 'done')
        self.assertEqual(move_middle.state, 'done')
        self.assertEqual(move_b.state, 'assigned')

        move_line_b = move_b.move_line_ids
        self.assertEqual(len(move_line_b), 1)
        self.assert_src_handover(move_line_b)
        self.assert_dest_highbay_1_2(move_line_b)
