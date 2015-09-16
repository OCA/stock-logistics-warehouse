# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Therp BV <http://therp.nl>
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
from openerp.tests.common import TransactionCase


class TestStockLogisticsWarehouse(TransactionCase):

    def test01_stock_levels(self):
        """checking that immediately_usable_qty actually reflects \
the variations in stock, both on product and template"""
        moveObj = self.env['stock.move']
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

        # Create a stock move from INCOMING to STOCK
        stockMoveInA = moveObj.create(
            {'location_id': supplier_location.id,
             'location_dest_id': stock_location.id,
             'name': 'MOVE INCOMING -> STOCK ',
             'product_id': productA.id,
             'product_uom': productA.uom_id.id,
             'product_uom_qty': 2,
             })

        stockMoveInB = moveObj.create(
            {'location_id': supplier_location.id,
             'location_dest_id': stock_location.id,
             'name': 'MOVE INCOMING -> STOCK ',
             'product_id': productB.id,
             'product_uom': productB.uom_id.id,
             'product_uom_qty': 3,
             })

        def compare_product_usable_qty(product, value):
            # Refresh, because the function field is not recalculated between
            # transactions
            product.refresh()
            self.assertEqual(product.immediately_usable_qty, value)

        compare_product_usable_qty(productA, 0)
        compare_product_usable_qty(templateAB, 0)

        stockMoveInA.action_confirm()
        compare_product_usable_qty(productA, 0)
        compare_product_usable_qty(templateAB, 0)

        stockMoveInA.action_assign()
        compare_product_usable_qty(productA, 0)
        compare_product_usable_qty(templateAB, 0)

        stockMoveInA.action_done()
        compare_product_usable_qty(productA, 2)
        compare_product_usable_qty(templateAB, 2)

        # will directly trigger action_done on productB
        stockMoveInB.action_done()
        compare_product_usable_qty(productA, 2)
        compare_product_usable_qty(productB, 3)
        compare_product_usable_qty(templateAB, 5)

        # Create a stock move from STOCK to CUSTOMER
        stockMoveOutA = moveObj.create(
            {'location_id': stock_location.id,
             'location_dest_id': customer_location.id,
             'name': ' STOCK --> CUSTOMER ',
             'product_id': productA.id,
             'product_uom': productA.uom_id.id,
             'product_uom_qty': 1,
             'state': 'confirmed',
             })

        stockMoveOutA.action_done()
        compare_product_usable_qty(productA, 1)
        compare_product_usable_qty(templateAB, 4)
