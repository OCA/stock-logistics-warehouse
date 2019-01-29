# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import UserError


class TestStockLocationRestrictGroup(common.TransactionCase):

    def setUp(self):
        super(TestStockLocationRestrictGroup, self).setUp()

        vals = {'name': 'OUT1',
                'group_restricted': True,
                'location_id': self.ref('stock.stock_location_locations')
                }
        self.stock_out_1 = self.env['stock.location'].create(vals)

        # PROCUREMENT GROUP 1
        vals = {'name': 'PROC1',
                'move_type': 'direct'
                }

        self.proc1 = self.env['procurement.group'].create(vals)

        # PROCUREMENT GROUP 2
        vals = {'name': 'PROC2',
                'move_type': 'direct'
                }

        self.proc2 = self.env['procurement.group'].create(vals)

        # MOVE 1
        vals = {'name': 'MOVE1',
                'group_id': self.proc1.id,
                'product_id': self.ref('product.product_product_6'),
                'product_uom': self.ref('product.product_uom_unit'),
                'product_uom_qty': 10.0,
                'picking_type_id': self.ref('stock.picking_type_in'),
                'location_id': self.ref('stock.stock_location_suppliers'),
                'location_dest_id': self.ref('stock.stock_location_locations')
                }

        self.move_1 = self.env['stock.move'].create(vals)

        # MOVE 2
        vals = {'name': 'MOVE2',
                'group_id': self.proc2.id,
                'product_id': self.ref('product.product_product_6'),
                'product_uom': self.ref('product.product_uom_unit'),
                'product_uom_qty': 10.0,
                'picking_type_id': self.ref('stock.picking_type_in'),
                'location_id': self.ref('stock.stock_location_suppliers'),
                'location_dest_id': self.ref('stock.stock_location_locations')
                }

        self.move_2 = self.env['stock.move'].create(vals)

        # PICKING 1
        vals = {'picking_type_id': self.ref('stock.picking_type_in'),
                'origin': 'TO_OUT1',
                'partner_id': self.ref('base.res_partner_1'),
                'location_id': self.ref('stock.stock_location_suppliers'),
                'location_dest_id': self.ref('stock.stock_location_locations'),
                'move_lines': [(4, [self.move_1.id])],
                }

        self.picking_1 = self.env['stock.picking'].create(vals)

        # PICKING 2
        vals = {'picking_type_id': self.ref('stock.picking_type_in'),
                'origin': 'TO_OUT1',
                'partner_id': self.ref('base.res_partner_1'),
                'location_id': self.ref('stock.stock_location_suppliers'),
                'location_dest_id': self.ref('stock.stock_location_locations'),
                'move_lines': [(4, [self.move_2.id])],
                }

        self.picking_2 = self.env['stock.picking'].create(vals)

        # OPERATION LINKED TO PICKING1
        vals = {'product_id': self.ref('product.product_product_6'),
                'product_qty': 10.0,
                'picking_id': self.picking_1.id,
                'product_uom_id': self.ref('product.product_uom_unit'),
                'location_id': self.ref('stock.stock_location_suppliers'),
                'location_dest_id': self.stock_out_1.id
                }
        self.pack_op_1 = self.env['stock.pack.operation'].create(vals)

        self.picking_1.write(
            {'pack_operation_ids': [(4, [self.pack_op_1.id])]})

        # OPERATION LINKED TO PICKING2
        vals = {'product_id': self.ref('product.product_product_6'),
                'product_qty': 10.0,
                'picking_id': self.picking_2.id,
                'product_uom_id': self.ref('product.product_uom_unit'),
                'location_id': self.ref('stock.stock_location_suppliers'),
                'location_dest_id': self.stock_out_1.id
                }
        self.pack_op_2 = self.env['stock.pack.operation'].create(vals)

        self.picking_2.write(
            {'pack_operation_ids': [(4, [self.pack_op_2.id])]})

    def test_00_restrict_location(self):
        # TRANSFER PICKING 1
        self.picking_1.action_confirm()
        self.picking_1.force_assign()
        self.picking_1.pack_operation_product_ids.write(
            {'qty_done': 10.0,
             'location_dest_id': self.stock_out_1.id})
        self.assertEqual(
            False,
            self.picking_2.move_lines[0].restricted)
        self.assertEqual(
            False,
            self.picking_2.pack_operation_ids[0].restricted)
        self.picking_1.do_new_transfer()

        # TRANSFER PICKING 2
        self.picking_2.action_confirm()
        self.picking_2.force_assign()
        self.picking_2.pack_operation_product_ids.write(
            {'qty_done': 10.0,
             'location_dest_id': self.stock_out_1.id})
        self.assertEqual(
            True,
            self.picking_2.pack_operation_ids[0].restricted)
        with self.assertRaises(UserError):
            self.picking_2.do_new_transfer()
        location = self.env['stock.location'].search(
            [('restricted_group', '=', 'PROC1')])
        self.assertEqual(1, len(location))

    def test_01_no_restrict_location(self):
        # Check normal process
        self.stock_out_1.group_restricted = False
        self.picking_1.action_confirm()
        self.picking_1.force_assign()
        self.picking_1.pack_operation_product_ids.write(
            {'qty_done': 10.0,
             'location_dest_id': self.stock_out_1.id})
        self.picking_1.do_new_transfer()

        self.assertEqual(self.stock_out_1.restricted_group,
                         self.env['procurement.group'])
        self.assertEqual(
            self.browse_ref('stock.stock_location_locations').restricted_group,
            self.env['procurement.group'])

    def test_02_restrict_move(self):
        # TRANSFER PICKING 1
        self.stock_out_1.group_restricted = True
        self.move_1.location_dest_id = self.stock_out_1
        self.picking_1.action_confirm()
        self.picking_1.force_assign()
        self.picking_1.pack_operation_product_ids.write(
            {'qty_done': 10.0,
             'location_dest_id': self.stock_out_1.id})
        self.assertEqual(
            False,
            self.picking_1.move_lines[0].restricted)
        self.picking_1.do_new_transfer()

        # TRANSFER PICKING 2
        self.move_2.location_dest_id = self.stock_out_1
        self.picking_2.location_dest_id = self.stock_out_1
        self.picking_2.action_confirm()
        self.picking_2.force_assign()
        self.picking_2.pack_operation_product_ids.write(
            {'qty_done': 10.0,
             'location_dest_id': self.stock_out_1.id})
        self.assertEqual(
            True,
            self.picking_2.move_lines[0].restricted)

    def test_03_test_return_button(self):
        self.assertEqual(
            False,
            self.env['stock.move'].restricted_move())
        self.assertEqual(
            False,
            self.env['stock.pack.operation'].restricted_op())
