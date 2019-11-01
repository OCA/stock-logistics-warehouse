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
            'location_id': cls.location_hb.id,
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

        Products must be a list of tuples (product, quantity, put_location).
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
            'location_dest_id': wh.lot_stock_id.id,
            'partner_id': self.partner_delta.id,
            'picking_type_id': wh.int_type_id.id,
        })

        for product, qty, put_location in products:
            dest = self.env['stock.move'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': product.uom_id.id,
                'picking_id': internal_picking.id,
                'location_id': wh.wh_input_stock_loc_id.id,
                'location_dest_id': put_location.id,
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

    def assert_dest_stock(self, record):
        self.assertEqual(record.location_dest_id, self.wh.lot_stock_id)

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

    def process_operations(self, moves):
        for move in moves:
            qty = move.move_line_ids.product_uom_qty
            move.move_line_ids.qty_done = qty
        move.mapped('picking_id').action_done()

    def test_change_location_to_routing_operation(self):
        in_picking, internal_picking = self._create_supplier_input_highbay(
            self.wh, [(self.product1, 10, self.location_hb_1_2)]
        )
        move_a = in_picking.move_lines
        move_b = internal_picking.move_lines
        self.assertEqual(move_a.state, 'assigned')
        self.process_operations(move_a)

        # At this point, we should have 3 stock.picking:
        #
        # +---------------------------------------------------------+
        # | IN/xxxx  Done                                           |
        # | Supplier -> Input                                       |
        # | Product1 Supplier → Input     (done) move_a             |
        # +---------------------------------------------------------+
        #
        # +-------------------------------------------------------------------+
        # | INT/xxxx Available                                                |
        # | Input → Stock                                                     |
        # | Product1 Input → Stock/Highbay/Handover  (available) move_b       |
        # +-------------------------------------------------------------------+
        #
        # the new one with our routing picking type:
        # +-------------------------------------------------------------------+
        # | HO/xxxx Waiting                                                   |
        # | Stock/Handover → Highbay                                          |
        # | Product1 Stock/Highbay/Handover → Highbay1-2 (waiting) added_move |
        # +-------------------------------------------------------------------+

        self.assert_src_supplier(move_a)
        self.assert_dest_input(move_a)
        self.assert_src_input(move_b)
        # the move stays B stays on the same dest location
        self.assert_dest_handover(move_b)

        # we should have a move added after move_b to put
        # the goods in their final location
        routing_move = move_b.move_dest_ids
        # the middle move stays in the same source location than the original
        # move: the move line will be in the sub-locations (handover)

        self.assert_src_handover(routing_move)
        self.assert_dest_highbay_1_2(routing_move)

        self.assertEquals(
            routing_move.picking_type_id,
            self.pick_type_routing_op
        )
        self.assertEquals(
            routing_move.picking_id.picking_type_id,
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
        self.assertEqual(move_b.state, 'assigned')
        self.assertEqual(routing_move.state, 'waiting')

        # we put the B move, to check that our new destination
        # move is correctly assigned
        self.process_operations(move_b)

        self.assertEqual(move_a.state, 'done')
        self.assertEqual(move_b.state, 'done')
        self.assertEqual(routing_move.state, 'assigned')

        routing_ml = routing_move.move_line_ids
        self.assertEqual(len(routing_ml), 1)
        self.assert_src_handover(routing_ml)
        self.assert_dest_highbay_1_2(routing_ml)

    def test_several_moves(self):
        in_picking, internal_picking = self._create_supplier_input_highbay(
            self.wh, [
                (self.product1, 10, self.location_hb_1_2),
                (self.product2, 10, self.location_shelf_1),
            ]
        )
        product1 = self.product1
        product2 = self.product2
        in_moves = in_picking.move_lines
        move_a_p1 = in_moves.filtered(lambda r: r.product_id == product1)
        move_a_p2 = in_moves.filtered(lambda r: r.product_id == product2)
        internal_moves = internal_picking.move_lines
        move_b_p1 = internal_moves.filtered(lambda r: r.product_id == product1)
        move_b_p2 = internal_moves.filtered(lambda r: r.product_id == product2)
        self.assertEqual(move_a_p1.state, 'assigned')
        self.assertEqual(move_a_p2.state, 'assigned')
        self.assertEqual(move_b_p1.state, 'waiting')
        self.assertEqual(move_b_p2.state, 'waiting')

        self.process_operations(move_a_p1 + move_a_p2)

        # At this point, we should have 3 stock.picking:
        #
        # +-----------------------------------------------------+
        # | IN/xxxx  Done                                       |
        # | Supplier -> Input                                   |
        # | Product1 Supplier → Input     (done) move_a_p1      |
        # | Product2 Supplier → Input     (done) move_a_p2      |
        # +-----------------------------------------------------+
        #
        # +-----------------------------------------------------------+
        # | INT/xxxx Available                                        |
        # | Input → Stock                                             |
        # | Product1 Input → Stock/Handover  (available) move_b_p1    |
        # | Product2 Input → Shelf1          (available) move_b_p2    |
        # +-----------------------------------------------------------+
        #
        # the new one with our routing picking type:
        # +-------------------------------------------------------------------+
        # | HO/xxxx Waiting                                                   |
        # | Stock/Handover → Highbay                                          |
        # | Product1 Stock/Highbay/Handover → Highbay1-2 (waiting) added_move |
        # +-------------------------------------------------------------------+

        routing_move = move_b_p1.move_dest_ids
        self.assertEqual(len(routing_move), 1)
        self.assertEqual(move_a_p1.move_dest_ids, move_b_p1)
        self.assertEqual(move_a_p2.move_dest_ids, move_b_p2)
        self.assertFalse(routing_move.move_dest_ids)
        self.assertFalse(move_b_p2.move_dest_ids)

        self.assertEqual(move_a_p1.state, 'done')
        self.assertEqual(move_a_p2.state, 'done')
        self.assertEqual(move_b_p1.state, 'assigned')
        self.assertEqual(move_b_p2.state, 'assigned')
        self.assertEqual(routing_move.state, 'waiting')

        routing_picking = routing_move.picking_id

        # Check picking A
        self.assertEqual(in_picking.move_lines, move_a_p1 + move_a_p2)
        self.assertEqual(in_picking.picking_type_id, self.wh.in_type_id)
        self.assert_src_supplier(in_picking)
        self.assert_dest_input(in_picking)

        # Check picking B
        self.assertEqual(
            internal_picking.move_lines,
            move_b_p1 + move_b_p2
        )
        self.assertEqual(
            internal_picking.picking_type_id,
            self.wh.int_type_id
        )
        self.assert_src_input(internal_picking)
        self.assert_dest_stock(internal_picking)

        # Check routing picking
        self.assertEqual(routing_picking.move_lines, routing_move)
        self.assertEqual(
            routing_picking.picking_type_id,
            self.pick_type_routing_op
        )
        self.assert_src_handover(routing_picking)
        self.assert_dest_highbay_1_2(routing_picking)

        # check move and move line A for product1
        self.assert_src_supplier(move_a_p1)
        self.assert_dest_input(move_a_p1)
        ml = move_a_p1.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_supplier(ml)
        self.assert_dest_input(ml)

        # check move and move line A for product2
        self.assert_src_supplier(move_a_p2)
        self.assert_dest_input(move_a_p2)
        ml = move_a_p2.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_supplier(ml)
        self.assert_dest_input(ml)

        # check move and move line B for product1
        self.assert_src_input(move_b_p1)
        self.assert_dest_handover(move_b_p1)
        ml = move_b_p1.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_input(ml)
        self.assert_dest_handover(ml)
        self.assertEqual(ml.state, 'assigned')

        # check move and move line B for product2
        self.assert_src_input(move_b_p2)
        self.assert_dest_shelf1(move_b_p2)
        ml = move_b_p2.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_input(ml)
        self.assert_dest_shelf1(ml)
        self.assertEqual(ml.state, 'assigned')

        # check routing move for product1
        self.assert_src_handover(routing_move)
        self.assert_dest_highbay_1_2(routing_move)

        # Deliver the internal picking (moves B),
        # the routing move for product1 should be assigned,
        # the product2 should be done (put in shelf1).
        self.process_operations(move_b_p1 + move_b_p2)

        self.assertEqual(move_b_p1.state, 'done')
        self.assertEqual(move_b_p2.state, 'done')
        self.assertEqual(routing_move.state, 'assigned')

        # Check move line for the routing move
        ml = routing_move.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_handover(ml)
        self.assert_dest_highbay_1_2(ml)

        self.process_operations(routing_move)

        self.assertEqual(move_a_p1.state, 'done')
        self.assertEqual(move_a_p2.state, 'done')
        self.assertEqual(move_b_p1.state, 'done')
        self.assertEqual(move_b_p2.state, 'done')
        self.assertEqual(routing_move.state, 'done')

    def test_several_move_lines(self):
        in_picking, internal_picking = self._create_supplier_input_highbay(
            self.wh, [
                (self.product1, 10, self.location_hb_1_2),
            ]
        )
        move_a = in_picking.move_lines
        move_b = internal_picking.move_lines
        # We do not want to trigger the routing operation now (see explanation
        # below)
        move_b.location_dest_id = self.wh.lot_stock_id

        self.process_operations(move_a)

        # At this point, move_a being 'done', action_assign is executed
        # on move_b. The standard put-away rules would put all the 10
        # products in a location. So with a standard odoo, we can't have
        # the situation we want to test here. Using additional modules
        # with more advanced put-away rules, the put-away could create
        # several move lines with different destinations, for instance
        # one in the highbay, one in the shelf. The highbay one will
        # need an additional move, the one in the shelf not.

        # In order to simulate this, we'll manually change the move lines of
        # move_b and call'_apply_dest_move_routing_operation()' on it to force
        # the application of the routing operation.

        first_ml = move_b.move_line_ids
        # use _write to bypass the changes to quants done in thex
        # write of stock.move.line: we want to keep the same reservation
        # of 10 units
        first_ml._write({
            'product_uom_qty': 6.0,
            'location_dest_id': self.location_hb_1_2.id,
        })
        move_b.move_line_ids.copy({
            'location_dest_id': self.location_shelf_1.id,
            'product_uom_qty': 4.0,
        })
        # At this point, we should have this
        #
        # +-----------------------------------------------------+
        # | IN/xxxx  Done                                       |
        # | Supplier -> Input                                   |
        # | 10x Product1 Supplier → Input     (done) move_a     |
        # +-----------------------------------------------------+
        #
        # +--------------------------------------------------------+
        # | INT/xxxx Available                                     |
        # | Input → Stock                                          |
        # | Move B Product1 Input → Stock with 2 operations:       |
        # | 6x Product1 Input → Stock/HB-1-2   (available)         |
        # | 4x Product1 Input → Stock/Shelf1   (available)         |
        # +--------------------------------------------------------+

        move_b._apply_dest_move_routing_operation()

        # We expect the routing operation to split the move_b so
        # we'll be able to have a move_dest_ids for the Highbay:

        # +--------------------------------------------------------+
        # | IN/xxxx  Done                                          |
        # | Supplier -> Input                                      |
        # | 10x Product1 Supplier → Input     (done) move_a        |
        # +--------------------------------------------------------+
        #
        # +--------------------------------------------------------+
        # | INT/xxxx Available                                     |
        # | Input → Stock                                          |
        # | 6x Product1 Input → Stock/Handover (available) move_b1 |
        # | 4x Product1 Input → Stock/Shelf1   (available) move_b2 |
        # +--------------------------------------------------------+
        #
        # the new one with our routing picking type:
        # +--------------------------------------------------------+
        # | HO/xxxx Waiting                                        |
        # | Stock/Handover → Highbay                               |
        # | 6x Product1 Stock/Highbay/Handover → HB-1-2 (waiting)  |
        # +--------------------------------------------------------+

        move_b_shelf = move_b
        move_b_handover = move_b.picking_id.move_lines - move_b
        self.assertEqual(len(move_b_handover), 1)

        routing_move = move_b_handover.move_dest_ids
        self.assertEqual(len(routing_move), 1)
        routing_picking = routing_move.picking_id

        # check chaining
        self.assertEqual(
            move_a.move_dest_ids,
            move_b_shelf + move_b_handover
        )
        self.assertFalse(move_b_shelf.move_dest_ids)
        self.assertEqual(move_b_handover.move_dest_ids, routing_move)
        self.assertFalse(routing_move.move_dest_ids)

        self.assertEqual(move_a.state, 'done')
        self.assertEqual(move_b_shelf.state, 'assigned')
        self.assertEqual(move_b_handover.state, 'assigned')
        self.assertEqual(routing_move.state, 'waiting')

        # Check picking A
        self.assertEqual(in_picking.move_lines, move_a)
        self.assertEqual(in_picking.picking_type_id, self.wh.in_type_id)
        self.assert_src_supplier(in_picking)
        self.assert_dest_input(in_picking)

        # Check picking B
        self.assertEqual(
            internal_picking.move_lines,
            move_b_shelf + move_b_handover
        )
        self.assertEqual(internal_picking.picking_type_id, self.wh.int_type_id)
        self.assert_src_input(internal_picking)
        self.assert_dest_stock(internal_picking)

        # Check routing picking
        self.assertEqual(
            routing_picking.move_lines,
            routing_move
        )
        self.assertEqual(
            routing_picking.picking_type_id,
            self.pick_type_routing_op
        )
        self.assert_src_handover(routing_picking)
        self.assert_dest_highbay_1_2(routing_picking)

        # check move and move line A
        self.assert_src_supplier(move_a)
        self.assert_dest_input(move_a)
        self.assertEqual(move_a.product_qty, 10.0)
        ml = move_a.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_supplier(ml)
        self.assert_dest_input(ml)
        self.assertEqual(ml.qty_done, 10.0)

        # check move and move line B Shelf
        self.assert_src_input(move_b_shelf)
        self.assert_dest_stock(move_b_shelf)
        self.assertEqual(move_b_shelf.product_qty, 4.0)
        ml = move_b_shelf.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_input(ml)
        self.assert_dest_shelf1(ml)
        self.assertEqual(ml.product_qty, 4.0)
        self.assertEqual(ml.qty_done, 0.0)

        # check move and move line B Handover
        self.assert_src_input(move_b_handover)
        self.assert_dest_handover(move_b_handover)
        self.assertEqual(move_b_handover.product_qty, 6.0)
        ml = move_b_handover.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_input(ml)
        self.assert_dest_handover(ml)
        self.assertEqual(ml.product_qty, 6.0)
        self.assertEqual(ml.qty_done, 0.0)

        # check routing move for product1
        self.assert_src_handover(routing_move)
        self.assert_dest_highbay_1_2(routing_move)

        # Deliver the internal picking (moves B),
        # the routing move should be assigned,
        # the other should be done (put in shelf1).
        self.process_operations(move_b_shelf + move_b_handover)

        self.assertEqual(move_b_shelf.state, 'done')
        self.assertEqual(move_b_handover.state, 'done')
        self.assertEqual(routing_move.state, 'assigned')

        # Check move line for the routing move
        ml = routing_move.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assert_src_handover(ml)
        self.assert_dest_highbay_1_2(ml)

        self.process_operations(routing_move)

        self.assertEqual(move_a.state, 'done')
        self.assertEqual(move_a.state, 'done')
        self.assertEqual(move_b_shelf.state, 'done')
        self.assertEqual(move_b_handover.state, 'done')
        self.assertEqual(routing_move.state, 'done')
