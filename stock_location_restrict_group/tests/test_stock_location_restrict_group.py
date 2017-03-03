# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestStockLocationRestrictGroup(common.TransactionCase):

    def setUp(self):
        super(TestStockLocationRestrictGroup, self).setUp()

        vals = {'name': 'OUT1',
                'usage': 'group',
                'location_id': self.ref('stock.stock_location_locations')
                }
        self.stock_out_1 = self.env['stock.location'].create(vals)

        vals = {'name': 'PROC1',
                'move_type': 'direct'
                }

        self.proc1 = self.env['procurement.group'].create(vals)

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

        vals = {'picking_type_id': self.ref('stock.picking_type_in'),
                'origin': 'TO_OUT1',
                'partner_id': self.ref('base.res_partner_1'),
                'location_id': self.ref('stock.stock_location_suppliers'),
                'location_dest_id': self.ref('stock.stock_location_locations'),
                'move_lines': [(4, [self.move_1.id])],
                }

        self.picking_1 = self.env['stock.picking'].create(vals)

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

    def test_00_restrict_location(self):
        self.picking_1.action_confirm()
        self.picking_1.force_assign()
        self.picking_1.pack_operation_product_ids.write(
            {'qty_done': 10.0,
             'location_dest_id': self.stock_out_1.id})
        self.picking_1.do_new_transfer()

        self.assertEqual(self.stock_out_1.restricted_group, self.proc1)
