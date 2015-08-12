# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common


class TestBackorderStrategy(common.TransactionCase):

    def setUp(self):
        """ Create the picking
        """
        super(TestBackorderStrategy, self).setUp()

        self.picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        self.picking_type = self.env.ref('stock.picking_type_in')

        product = self.env.ref('product.product_product_36')
        loc_supplier_id = self.env.ref('stock.stock_location_suppliers').id
        loc_stock_id = self.env.ref('stock.stock_location_stock').id

        self.picking = self.picking_obj.create(
            {'picking_type_id': self.picking_type.id})
        move_obj.create({'name': '/',
                         'picking_id': self.picking.id,
                         'product_uom': product.uom_id.id,
                         'location_id': loc_supplier_id,
                         'location_dest_id': loc_stock_id,
                         'product_id': product.id,
                         'product_uom_qty': 2})
        self.picking.action_confirm()

    def _process_picking(self):
        """ Receive partially the picking
        """
        wiz_detail_obj = self.env['stock.transfer_details']
        wiz_detail = wiz_detail_obj.with_context(
            active_model='stock.picking',
            active_ids=[self.picking.id],
            active_id=self.picking.id).create({'picking_id': self.picking.id})
        wiz_detail.item_ids[0].quantity = 1
        wiz_detail.do_detailed_transfer()

    def test_backorder_strategy_create(self):
        """ Check strategy for stock.picking_type_in is create
            Receive picking
            Check backorder is created
        """
        self.assertEqual('create', self.picking_type.backorder_strategy)
        self._process_picking()
        backorder = self.picking_obj.search(
            [('backorder_id', '=', self.picking.id)])
        self.assertTrue(backorder)

    def test_backorder_strategy_no_create(self):
        """ Set strategy for stock.picking_type_in to no_create
            Receive picking
            Check there is no backorder
        """
        self.picking_type.backorder_strategy = 'no_create'
        self._process_picking()
        backorder = self.picking_obj.search(
            [('backorder_id', '=', self.picking.id)])
        self.assertFalse(backorder)

    def test_backorder_strategy_cancel(self):
        """ Set strategy for stock.picking_type_in to cancel
            Receive picking
            Check the backorder state is cancel
        """
        self.picking_type.backorder_strategy = 'cancel'
        self._process_picking()
        backorder = self.picking_obj.search(
            [('backorder_id', '=', self.picking.id)])
        self.assertTrue(backorder)
        self.assertEqual('cancel', backorder[0].state)
