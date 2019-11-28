# Copyright 2019 Camptocamp (https://www.camptocamp.com)

from odoo.tests import common


class TestSourceRoutingOperation(common.SavepointCase):

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

        cls.customer_loc = cls.env.ref('stock.stock_location_customers')
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
            'default_location_src_id': cls.location_hb.id,
            'default_location_dest_id': cls.location_handover.id,
            'sequence_id': picking_type_sequence.id,
        })
        cls.location_hb.write({
            'src_routing_picking_type_id': cls.pick_type_routing_op.id
        })

    def _create_pick_ship(self, wh, products=None):
        """Create pick+ship pickings

        Products must be a list of tuples (product, quantity).
        One stock move will be create for each tuple.
        """
        if products is None:
            products = []
        customer_picking = self.env['stock.picking'].create({
            'location_id': wh.wh_output_stock_loc_id.id,
            'location_dest_id': self.customer_loc.id,
            'partner_id': self.partner_delta.id,
            'picking_type_id': wh.out_type_id.id,
        })

        pick_picking = self.env['stock.picking'].create({
            'location_id': wh.lot_stock_id.id,
            'location_dest_id': wh.wh_output_stock_loc_id.id,
            'partner_id': self.partner_delta.id,
            'picking_type_id': wh.pick_type_id.id,
        })

        for product, qty in products:
            dest = self.env['stock.move'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': product.uom_id.id,
                'picking_id': customer_picking.id,
                'location_id': wh.wh_output_stock_loc_id.id,
                'location_dest_id': self.customer_loc.id,
                'state': 'waiting',
                'procure_method': 'make_to_order',
            })

            self.env['stock.move'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': product.uom_id.id,
                'picking_id': pick_picking.id,
                'location_id': wh.lot_stock_id.id,
                'location_dest_id': wh.wh_output_stock_loc_id.id,
                'move_dest_ids': [(4, dest.id)],
                'state': 'confirmed',
            })
        return pick_picking, customer_picking

    def _update_product_qty_in_location(self, location, product, quantity):
        self.env['stock.quant']._update_available_quantity(
            product, location, quantity
        )

    def assert_src_stock(self, record):
        self.assertEqual(record.location_id, self.wh.lot_stock_id)

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
        self.assertEqual(record.location_destid, self.location_hb_1_2)

    def assert_src_output(self, record):
        self.assertEqual(record.location_id, self.wh.wh_output_stock_loc_id)

    def assert_dest_output(self, record):
        self.assertEqual(record.location_dest_id,
                         self.wh.wh_output_stock_loc_id)

    def assert_dest_customer(self, record):
        self.assertEqual(record.location_dest_id, self.customer_loc)

    def process_operations(self, move):
        qty = move.move_line_ids.product_uom_qty
        move.move_line_ids.qty_done = qty
        move.picking_id.action_done()

    def test_change_location_to_routing_operation(self):
        pick_picking, customer_picking = self._create_pick_ship(
            self.wh, [(self.product1, 10)]
        )
        move_a = pick_picking.move_lines
        move_b = customer_picking.move_lines

        self._update_product_qty_in_location(
            self.location_hb_1_2, move_a.product_id, 100
        )
        pick_picking.action_assign()

        ml = move_a.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_highbay_1_2(ml)
        self.assert_dest_handover(ml)

        self.assertEqual(
            ml.picking_id.picking_type_id, self.pick_type_routing_op
        )

        self.assert_src_stock(move_a)
        self.assert_dest_handover(move_a)
        # the move stays B stays on the same source location
        self.assert_src_output(move_b)
        self.assert_dest_customer(move_b)

        move_middle = move_a.move_dest_ids
        # the routing move stays in the same source location than the original
        # move: the move line will be in the sub-locations (handover)

        self.assert_src_stock(move_middle)
        # Output
        self.assert_dest_output(move_middle)

        self.assert_src_stock(move_a.picking_id)
        self.assert_dest_handover(move_a.picking_id)

        self.assertEqual(move_a.state, 'assigned')
        self.assertEqual(move_middle.state, 'waiting')
        self.assertEqual(move_b.state, 'waiting')

        # we deliver move A to check that our middle move line properly takes
        # goods from the handover
        self.process_operations(move_a)
        self.assertEqual(move_a.state, 'done')
        self.assertEqual(move_middle.state, 'assigned')
        self.assertEqual(move_b.state, 'waiting')

        move_line_middle = move_middle.move_line_ids
        self.assertEqual(len(move_line_middle), 1)
        self.assert_src_handover(move_line_middle)
        self.assert_dest_output(move_line_middle)

    def test_several_moves(self):
        pick_picking, customer_picking = self._create_pick_ship(
            self.wh, [(self.product1, 10), (self.product2, 10)]
        )
        product1 = self.product1
        product2 = self.product2
        # in Highbay → should generate a new operation in Highbay picking type
        self._update_product_qty_in_location(
            self.location_hb_1_2, self.product1, 20
        )
        # another product in a shelf, no additional operation for this one
        self._update_product_qty_in_location(
            self.location_shelf_1, self.product2, 20
        )
        pick_moves = pick_picking.move_lines
        move_a_p1 = pick_moves.filtered(lambda r: r.product_id == product1)
        move_a_p2 = pick_moves.filtered(lambda r: r.product_id == product2)
        cust_moves = customer_picking.move_lines
        move_b_p1 = cust_moves.filtered(lambda r: r.product_id == product1)
        move_b_p2 = cust_moves.filtered(lambda r: r.product_id == product2)

        pick_picking.action_assign()

        # At this point, we should have 3 stock.picking:
        #
        # +-------------------------------------------------------------------+
        # | HO/xxxx  Assigned                                                 |
        # | Stock → Stock/Handover                                            |
        # | Product1 Highbay/Bay1/Bin1 → Stock/Handover (available) move_a_p1 |
        # +-------------------------------------------------------------------+
        #
        # +------------------------------------------------------------------+
        # | PICK/xxxx Waiting                                                |
        # | Stock → Output                                                   |
        # | Product1 Stock/Handover → Output (waiting)   move_middle (added) |
        # | Product2 Stock/Shelf1   → Output (available) move_a_p2           |
        # +------------------------------------------------------------------+
        #
        # +------------------------------------------------+
        # | OUT/xxxx Waiting                               |
        # | Output → Customer                              |
        # | Product1 Output → Customer (waiting) move_b_p1 |
        # | Product2 Output → Customer (waiting) move_b_p2 |
        # +------------------------------------------------+

        move_middle = move_a_p1.move_dest_ids
        self.assertEqual(len(move_middle), 1)

        self.assertFalse(move_a_p1.move_orig_ids)
        self.assertEqual(move_middle.move_dest_ids, move_b_p1)
        self.assertFalse(move_a_p2.move_orig_ids)
        self.assertEqual(move_a_p2.move_dest_ids, move_b_p2)

        ml = move_a_p1.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_highbay_1_2(ml)
        self.assert_dest_handover(ml)
        # this is a new HO picking
        self.assertEqual(
            ml.picking_id.picking_type_id, self.pick_type_routing_op
        )
        self.assertEqual(ml.state, 'assigned')

        # this one stays in the PICK/
        ml = move_a_p2.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_shelf1(ml)
        self.assert_dest_output(ml)
        self.assertEqual(ml.picking_id.picking_type_id, self.wh.pick_type_id)
        self.assertEqual(ml.state, 'assigned')

        # the move stays B stays on the same source location
        self.assert_src_output(move_b_p1)
        self.assert_dest_customer(move_b_p1)
        self.assertEqual(move_b_p1.state, 'waiting')
        self.assert_src_output(move_b_p2)
        self.assert_dest_customer(move_b_p2)
        self.assertEqual(move_b_p2.state, 'waiting')

        # Check middle move
        # Stock
        self.assert_src_stock(move_middle)
        # Output
        self.assert_dest_output(move_middle)
        self.assert_src_stock(move_middle.picking_id)
        # we deliver move A to check that our middle move line properly takes
        # goods from the handover
        self.process_operations(move_a_p1)

        self.assertEqual(move_a_p1.state, 'done')
        self.assertEqual(move_a_p2.state, 'assigned')
        self.assertEqual(move_middle.state, 'assigned')
        self.assertEqual(move_b_p1.state, 'waiting')
        self.assertEqual(move_b_p2.state, 'waiting')

        move_line_middle = move_middle.move_line_ids
        self.assertEqual(len(move_line_middle), 1)
        # Handover
        self.assert_src_handover(move_line_middle)
        # Output
        self.assert_dest_output(move_line_middle)

        self.process_operations(move_middle)
        self.process_operations(move_a_p2)

        self.assertEqual(move_a_p1.state, 'done')
        self.assertEqual(move_a_p2.state, 'done')
        self.assertEqual(move_middle.state, 'done')
        self.assertEqual(move_b_p1.state, 'assigned')
        self.assertEqual(move_b_p2.state, 'assigned')

        self.process_operations(move_b_p1)
        self.process_operations(move_b_p2)

        self.assertEqual(move_a_p1.state, 'done')
        self.assertEqual(move_a_p2.state, 'done')
        self.assertEqual(move_middle.state, 'done')
        self.assertEqual(move_b_p1.state, 'done')
        self.assertEqual(move_b_p2.state, 'done')

    def test_several_move_lines(self):
        pick_picking, customer_picking = self._create_pick_ship(
            self.wh, [(self.product1, 10)]
        )
        move_a = pick_picking.move_lines
        move_b = customer_picking.move_lines
        # in Highbay → should generate a new operation in Highbay picking type
        self._update_product_qty_in_location(
            self.location_hb_1_2, move_a.product_id, 6
        )
        # same product in a shelf, we should have a second move line directly
        # picked from the shelf without additional operation for the Highbay
        self._update_product_qty_in_location(
            self.location_shelf_1, move_a.product_id, 4
        )

        pick_picking.action_assign()
        # it splits the stock move to be able to chain the quantities from
        # the Highbay
        self.assertEqual(len(pick_picking.move_lines), 2)
        move_a1 = pick_picking.move_lines.filtered(
            lambda move: move.product_uom_qty == 4
        )
        move_a2 = pick_picking.move_lines.filtered(
            lambda move: move.product_uom_qty == 6
        )
        move_ho = move_a2.move_orig_ids
        self.assertTrue(move_ho)

        # At this point, we should have 3 stock.picking:
        #
        # +-------------------------------------------------------------------+
        # | HO/xxxx  Assigned                                                 |
        # | Stock → Stock/Handover                                            |
        # | 6x Product Highbay/Bay1/Bin1 → Stock/Handover (available) move_ho |
        # +-------------------------------------------------------------------+
        #
        # +-------------------------------------------------------------------+
        # | PICK/xxxx Waiting                                                 |
        # | Stock → Output                                                    |
        # | 6x Product Stock/Handover → Output (waiting)   move_a2 (split)    |
        # | 4x Product Stock/Shelf1   → Output (available) move_a1            |
        # +-------------------------------------------------------------------+
        #
        # +-------------------------------------------------+
        # | OUT/xxxx Waiting                                |
        # | Output → Customer                               |
        # | 10x Product Output → Customer (waiting) move_b  |
        # +-------------------------------------------------+

        self.assertFalse(move_a1.move_orig_ids)
        self.assertEqual(move_ho.move_dest_ids, move_a2)

        ml = move_a1.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_shelf1(ml)
        self.assert_dest_output(ml)
        self.assertEqual(ml.picking_id.picking_type_id, self.wh.pick_type_id)
        self.assertEqual(ml.state, 'assigned')

        ml = move_ho.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_highbay_1_2(ml)
        self.assert_dest_handover(ml)
        # this is a new HO picking
        self.assertEqual(
            ml.picking_id.picking_type_id, self.pick_type_routing_op
        )
        self.assertEqual(ml.state, 'assigned')

        # the split move is waiting for 'move_ho'
        self.assertEqual(len(ml), 1)
        self.assert_src_stock(move_a2)
        self.assert_dest_output(move_a2)
        self.assertEqual(
            move_a2.picking_id.picking_type_id,
            self.wh.pick_type_id
        )
        self.assertEqual(move_a2.state, 'waiting')

        # the move stays B stays identical
        self.assert_src_output(move_b)
        self.assert_dest_customer(move_b)
        self.assertEqual(move_b.state, 'waiting')

        # we deliver HO picking to check that our middle move line properly
        # takes goods from the handover
        self.process_operations(move_ho)

        self.assertEqual(move_ho.state, 'done')
        self.assertEqual(move_a1.state, 'assigned')
        self.assertEqual(move_a2.state, 'assigned')
        self.assertEqual(move_b.state, 'waiting')

        self.process_operations(move_a1)
        self.process_operations(move_a2)

        self.assertEqual(move_ho.state, 'done')
        self.assertEqual(move_a1.state, 'done')
        self.assertEqual(move_a2.state, 'done')
        self.assertEqual(move_b.state, 'assigned')

        self.process_operations(move_b)
        self.assertEqual(move_ho.state, 'done')
        self.assertEqual(move_a1.state, 'done')
        self.assertEqual(move_a2.state, 'done')
        self.assertEqual(move_b.state, 'done')
