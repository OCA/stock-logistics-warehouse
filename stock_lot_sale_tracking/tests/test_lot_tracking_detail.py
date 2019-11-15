# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import common


class TestLotTrackingDetail(common.TransactionCase):

    def setUp(self):
        super(TestLotTrackingDetail, self).setUp()
        self.sale_obj = self.env['sale.order']
        self.sale_line_obj = self.env['sale.order.line']
        self.chg_qty_obj = self.env['stock.change.product.qty']
        self.lot_icecream = self.env.ref('stock.lot_icecream_0')
        self.lot_icecream_1 = self.env.ref('stock.lot_icecream_1')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.picking_type_out.use_existing_lots = True
        self.partner_1 = self.env.ref('base.res_partner_1')
        self.shipping_1 = self.env.ref('base.res_partner_address_1')
        self.stock = self.env.ref('stock.stock_location_stock')
        self.lot_icecream.product_id.tracking = 'lot'
        vals = {
            'partner_id': self.partner_1.id,
            'partner_shipping_id': self.shipping_1.id,
        }
        self.order = self.sale_obj.create(vals)
        vals = {
            'order_id': self.order.id,
            'product_id': self.lot_icecream.product_id.id,
            'product_uom_qty': 5.0,
            'product_uom': self.lot_icecream.product_id.uom_id.id,
        }
        self.line_1 = self.sale_line_obj.create(vals)

        vals = {
            'product_id': self.lot_icecream.product_id.id,
            'new_quantity': 2.0,
            'lot_id': self.lot_icecream.id,
            'location_id': self.stock.id,
        }
        wizard = self.chg_qty_obj.create(vals)
        wizard.change_product_qty()

        vals = {
            'product_id': self.lot_icecream.product_id.id,
            'new_quantity': 3.0,
            'lot_id': self.lot_icecream_1.id,
            'location_id': self.stock.id,
        }
        wizard = self.chg_qty_obj.create(vals)
        wizard.change_product_qty()

    def test_lot_tracking(self):
        self.order.action_confirm()
        pickings = self.order.picking_ids.filtered(
            lambda p: p.location_dest_id.usage == 'customer')
        self.assertEquals(
            1,
            len(pickings)
        )
        self.assertEquals(
            2,
            len(pickings.pack_operation_product_ids.pack_lot_ids)
        )
        for pack_lot in pickings.pack_operation_product_ids.pack_lot_ids:
            if pack_lot.lot_id == self.lot_icecream:
                pack_lot.qty = 2.0
            if pack_lot.lot_id == self.lot_icecream_1:
                pack_lot.qty = 3.0
        pickings.action_done()
        self.assertEquals(
            2,
            self.order.sale_lot_tracking_count
        )
        self.assertEquals(
            2,
            len(self.order.sale_lot_tracking_ids)
        )
