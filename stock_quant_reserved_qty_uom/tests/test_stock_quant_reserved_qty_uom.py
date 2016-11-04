# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestStockQuantReservedQtyUom(TransactionCase):

    def test01(self):
        """checking that the reserved_qty_uom is expressed in the unit of
        measure of the reservation move."""
        pickingObj = self.env['stock.picking']
        productObj = self.env['product.product']
        supplier_location = self.env.ref('stock.stock_location_suppliers')
        stock_location = self.env.ref('stock.stock_location_stock')
        customer_location = self.env.ref('stock.stock_location_customers')
        uom_unit = self.env.ref('product.product_uom_unit')
        uom_dozen = self.env.ref('product.product_uom_dozen')

        # Create product A
        productA = productObj.create(
            {'name': 'product A',
             'standard_price': 1.0,
             'type': 'product',
             'uom_id': uom_unit.id,
             'default_code': 'A',
             })

        # Create a picking move from INCOMING to STOCK
        pickingInA = pickingObj.create({
            'picking_type_id': self.ref('stock.picking_type_in'),
            'location_id': supplier_location.id,
            'location_dest_id': stock_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': productA.id,
                    'product_uom': productA.uom_id.id,
                    'product_uom_qty': 12.0,
                    'location_id': supplier_location.id,
                    'location_dest_id': stock_location.id,
                })]
        })

        pickingInA.action_confirm()
        pickingInA.action_assign()
        pickingInA.action_done()

        # Create a picking from STOCK to CUSTOMER
        pickingOutA = pickingObj.create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': productA.id,
                    'product_uom': uom_dozen.id,
                    'product_uom_qty': 1.0,
                    'location_id': stock_location.id,
                    'location_dest_id': customer_location.id,
                })]
        })
        pickingOutA.action_confirm()
        pickingOutA.action_assign()

        for move in pickingOutA.move_lines:
            for quant in move.reserved_quant_ids:
                quant._compute_reserved_qty_uom()
                self.assertEqual(quant.reserved_qty_uom, 1)
                self.assertEqual(quant.qty, 12)
