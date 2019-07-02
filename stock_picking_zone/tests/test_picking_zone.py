# Copyright 2019 Camptocamp (https://www.camptocamp.com)

from odoo.tests import common


class TestPickingZone(common.SavepointCase):

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
        cls.location_hb_1 = cls.env['stock.location'].create({
            'name': 'Highbay Shelve 1',
            'location_id': cls.location_hb.id,
        })
        cls.location_hb_1_1 = cls.env['stock.location'].create({
            'name': 'Highbay Shelve 1 Bin 1',
            'location_id': cls.location_hb_1.id,
        })
        cls.location_hb_1_2 = cls.env['stock.location'].create({
            'name': 'Highbay Shelve 1 Bin 2',
            'location_id': cls.location_hb_1.id,
        })

        cls.location_handover = cls.env['stock.location'].create({
            'name': 'Handover',
            'location_id': cls.wh.view_location_id.id,
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'Product A', 'type': 'product',
        })

        picking_type_sequence = cls.env['ir.sequence'].create({
            'name': 'WH/Handover',
            'prefix': 'WH/HO/',
            'padding': 5,
            'company_id': cls.wh.company_id.id,
        })
        cls.pick_type_zone = cls.env['stock.picking.type'].create({
            'name': 'Zone',
            'code': 'internal',
            'use_create_lots': False,
            'use_existing_lots': True,
            'default_location_src_id': cls.location_hb.id,
            'default_location_dest_id': cls.location_handover.id,
            'is_zone': True,
            'sequence_id': picking_type_sequence.id,
        })

    def _create_pick_ship(self, wh):
        customer_picking = self.env['stock.picking'].create({
            'location_id': wh.wh_output_stock_loc_id.id,
            'location_dest_id': self.customer_loc.id,
            'partner_id': self.partner_delta.id,
            'picking_type_id': wh.out_type_id.id,
        })
        dest = self.env['stock.move'].create({
            'name': self.product_a.name,
            'product_id': self.product_a.id,
            'product_uom_qty': 10,
            'product_uom': self.product_a.uom_id.id,
            'picking_id': customer_picking.id,
            'location_id': wh.wh_output_stock_loc_id.id,
            'location_dest_id': self.customer_loc.id,
            'state': 'waiting',
            'procure_method': 'make_to_order',
        })

        pick_picking = self.env['stock.picking'].create({
            'location_id': wh.lot_stock_id.id,
            'location_dest_id': wh.wh_output_stock_loc_id.id,
            'partner_id': self.partner_delta.id,
            'picking_type_id': wh.pick_type_id.id,
        })

        self.env['stock.move'].create({
            'name': self.product_a.name,
            'product_id': self.product_a.id,
            'product_uom_qty': 10,
            'product_uom': self.product_a.uom_id.id,
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

    def test_change_location_to_zone(self):

        pick_picking, customer_picking = self._create_pick_ship(self.wh)
        move_a = pick_picking.move_lines
        move_b = customer_picking.move_lines

        self._update_product_qty_in_location(
            self.location_hb_1_2, move_a.product_id, 100
        )
        pick_picking.action_assign()

        ml = move_a.move_line_ids
        self.assertEqual(len(ml), 1)
        self.assertEqual(ml.location_id, self.location_hb_1_2)
        self.assertEqual(ml.location_dest_id, self.location_handover)

        self.assertEqual(ml.picking_id.picking_type_id, self.pick_type_zone)

        self.assertEqual(move_a.location_id, self.wh.lot_stock_id)
        self.assertEqual(move_a.location_dest_id, self.location_handover)
        # the move stays B stays on the same source location (sticky)
        self.assertEqual(move_b.location_id, self.wh.wh_output_stock_loc_id)
        self.assertEqual(move_b.location_dest_id, self.customer_loc)

        move_middle = move_a.move_dest_ids
        self.assertEqual(move_middle.location_id, move_a.location_dest_id)
        self.assertEqual(move_middle.location_dest_id, move_b.location_id)

        self.assertEqual(
            move_a.picking_id.location_dest_id,
            self.location_handover
        )
        self.assertEqual(
            move_middle.picking_id.location_id,
            self.location_handover
        )

        self.assertEqual(move_a.state, 'assigned')
        self.assertEqual(move_middle.state, 'waiting')
        self.assertEqual(move_b.state, 'waiting')
