# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockLogisticsWarehouse(TransactionCase):
    def test_res_config(self):
        """Test the config file"""
        stock_setting = self.env['res.config.settings'].create({})

        self.assertEquals(
            stock_setting.stock_available_mrp_based_on,
            'qty_available')
        stock_setting.stock_available_mrp_based_on = 'immediately_usable_qty'
        stock_setting.set_values()
        self.assertEquals(
            stock_setting.stock_available_mrp_based_on,
            'immediately_usable_qty')

    def test01_stock_levels(self):
        """checking that immediately_usable_qty actually reflects \
           the variations in stock, both on product and template"""
        moveObj = self.env['stock.move']
        productObj = self.env['product.product']
        templateObj = self.env['product.template']
        supplier_location = self.env.ref('stock.stock_location_suppliers')
        stock_location = self.env.ref('stock.stock_location_stock')
        customer_location = self.env.ref('stock.stock_location_customers')
        uom_unit = self.env.ref('uom.product_uom_unit')

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
            """
            Compare the immediately_usable_qty with the given value
            Check also the search function for the immediately_usable_qty field
            :param product: product (template/product) recordset
            :param value: int
            :return:
            """
            # Refresh, because the function field is not recalculated between
            # transactions
            product.refresh()
            self.assertEqual(product.immediately_usable_qty, value)
            # Now check search function
            domain = [('immediately_usable_qty', '=', value)]
            results = self.env[product._name].search(domain)
            self.assertIn(product.id, results.ids)
            domain = [('immediately_usable_qty', '!=', value)]
            results = self.env[product._name].search(domain)
            self.assertNotIn(product.id, results.ids)
            domain = [('immediately_usable_qty', '>', value-1)]
            results = self.env[product._name].search(domain)
            self.assertIn(product.id, results.ids)
            domain = [('immediately_usable_qty', '<', value+1)]
            results = self.env[product._name].search(domain)
            self.assertIn(product.id, results.ids)

        compare_product_usable_qty(productA, 0)
        compare_product_usable_qty(templateAB, 0)

        stockMoveInA._action_confirm()
        compare_product_usable_qty(productA, 2)
        compare_product_usable_qty(templateAB, 2)

        stockMoveInA._action_assign()
        compare_product_usable_qty(productA, 2)
        compare_product_usable_qty(templateAB, 2)

        stockMoveInA._action_done()
        compare_product_usable_qty(productA, 2)
        compare_product_usable_qty(templateAB, 2)

        # will directly trigger action_done on productB
        stockMoveInB._action_done()
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

        stockMoveOutA._action_done()
        compare_product_usable_qty(productA, 1)
        compare_product_usable_qty(templateAB, 4)

        # Potential Qty is set as 0.0 by default
        self.assertEquals(templateAB.potential_qty, 0.0)
        self.assertEquals(productA.potential_qty, 0.0)
