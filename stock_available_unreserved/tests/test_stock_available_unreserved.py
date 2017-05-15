# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockLogisticsWarehouse(TransactionCase):

    def test01_stock_levels(self):
        """checking that qty_available_not_res actually reflects \
        the variations in stock, both on product and template"""
        pickingObj = self.env['stock.picking']
        productObj = self.env['product.product']
        templateObj = self.env['product.template']
        supplier_location = self.env.ref('stock.stock_location_suppliers')
        stock_location = self.env.ref('stock.stock_location_stock')
        customer_location = self.env.ref('stock.stock_location_customers')
        uom_unit = self.env.ref('product.product_uom_unit')

        # Create product template
        templateAB = templateObj.create(
            {'name': 'templAB',
             'uom_id': uom_unit.id,
             })

        # Create product A and B
        productA = productObj.create(
            {'name': 'product A',
             'standard_price': 1,
             'type': 'product',
             'uom_id': uom_unit.id,
             'default_code': 'A',
             'product_tmpl_id': templateAB.id,
             })

        productB = productObj.create(
            {'name': 'product B',
             'standard_price': 1,
             'type': 'product',
             'uom_id': uom_unit.id,
             'default_code': 'B',
             'product_tmpl_id': templateAB.id,
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
                    'product_uom_qty': 2,
                    'location_id': supplier_location.id,
                    'location_dest_id': stock_location.id,
                })]
        })

        pickingInB = pickingObj.create({
            'picking_type_id': self.ref('stock.picking_type_in'),
            'location_id': supplier_location.id,
            'location_dest_id': stock_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': productB.id,
                    'product_uom': productB.uom_id.id,
                    'product_uom_qty': 3,
                    'location_id': supplier_location.id,
                    'location_dest_id': stock_location.id,
                })]
        })

        def compare_qty_available_not_res(product, value):
            # Refresh, because the function field is not recalculated between
            # transactions
            product.refresh()
            self.assertEqual(product.qty_available_not_res, value)

        compare_qty_available_not_res(productA, 0)
        compare_qty_available_not_res(templateAB, 0)

        pickingInA.action_confirm()
        compare_qty_available_not_res(productA, 0)
        compare_qty_available_not_res(templateAB, 0)

        pickingInA.action_assign()
        compare_qty_available_not_res(productA, 0)
        compare_qty_available_not_res(templateAB, 0)

        pickingInA.action_done()
        compare_qty_available_not_res(productA, 2)
        compare_qty_available_not_res(templateAB, 2)

        # will directly trigger action_done on productB
        pickingInB.action_done()
        compare_qty_available_not_res(productA, 2)
        compare_qty_available_not_res(productB, 3)
        compare_qty_available_not_res(templateAB, 5)

        # Create a picking from STOCK to CUSTOMER
        pickingOutA = pickingObj.create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': productB.id,
                    'product_uom': productB.uom_id.id,
                    'product_uom_qty': 2,
                    'location_id': stock_location.id,
                    'location_dest_id': customer_location.id,
                })]
        })

        compare_qty_available_not_res(productB, 3)
        compare_qty_available_not_res(templateAB, 5)

        pickingOutA.action_confirm()
        compare_qty_available_not_res(productB, 3)
        compare_qty_available_not_res(templateAB, 5)

        pickingOutA.action_assign()
        compare_qty_available_not_res(productB, 1)
        compare_qty_available_not_res(templateAB, 3)

        pickingOutA.action_done()
        compare_qty_available_not_res(productB, 1)
        compare_qty_available_not_res(templateAB, 3)

        templateAB.action_open_quants_unreserved()
