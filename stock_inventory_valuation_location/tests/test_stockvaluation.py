from odoo.tests.common import TransactionCase


class TestStockValuation(TransactionCase):
    def setUp(self):
        super(TestStockValuation, self).setUp()
        self.stock_location1 = self.env.ref('stock.stock_location_stock')
        self.stock_location2 = self.env.ref('stock.stock_location_shop0')
        self.stock_location3 = self.env.ref('stock.stock_location_components')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.inventory_location = self.env.ref('stock.location_inventory')
        self.partner = self.env['res.partner'].create({'name': 'xxx'})
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.product1 = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'default_code': 'prda',
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.product1.product_tmpl_id.standard_price = 10.0
        self.product1.product_tmpl_id.valuation = 'real_time'
        account = self.env['account.account']
        self.stock_input_account = account.create({
            'name': 'Stock Input',
            'code': 'StockIn',
            'user_type_id': self.env.ref('account.data_account_type_current_assets').id,
        })
        self.stock_output_account = account.create({
            'name': 'Stock Output',
            'code': 'StockOut',
            'user_type_id': self.env.ref('account.data_account_type_current_assets').id,
        })
        self.stock_valuation_account = account.create({
            'name': 'Stock Valuation',
            'code': 'Stock Valuation',
            'user_type_id': self.env.ref('account.data_account_type_current_assets').id,
        })
        self.stock_journal = self.env['account.journal'].create({
            'name': 'Stock Journal',
            'code': 'STJTEST',
            'type': 'general',
        })

        self.product1.categ_id.write({
            'property_stock_account_input_categ_id': self.stock_input_account.id,
            'property_stock_account_output_categ_id': self.stock_output_account.id,
            'property_stock_valuation_account_id': self.stock_valuation_account.id,
            'property_stock_journal': self.stock_journal.id,
        })

    def test_cost_method_standard(self):
        self.product1.categ_id.property_cost_method = 'standard'

        # receive 15 units in location 1
        move1 = self.env['stock.move'].create({
            'name': 'Receive 15 units at 10',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location1.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 15.0,
            'price_unit': 10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done = 15.0
        move1._action_done()

        # receive 10 units in location 2
        move2 = self.env['stock.move'].create({
            'name': 'Receive 10 units at 15',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location2.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 10.0,
            'price_unit': 15,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done = 10.0
        move2._action_done()

        # sell 5 units of location 1
        move3 = self.env['stock.move'].create({
            'name': 'Deliver 5 units',
            'location_id': self.stock_location1.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 5.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done = 5.0
        move3._action_done()

        # sell 5 units of location 2
        move4 = self.env['stock.move'].create({
            'name': 'Deliver 5 units',
            'location_id': self.stock_location2.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 5.0,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done = 5.0
        move4._action_done()

        quant1 = self.env['stock.quant'].read_group([
            ('product_id', '=', self.product1.id),
            ('location_id', '=', self.stock_location1.id)],
            ['value'], ['location_id'])[0]
        quant2 = self.env['stock.quant'].read_group([
            ('product_id', '=', self.product1.id),
            ('location_id', '=', self.stock_location2.id)],
            ['value'], ['location_id'])[0]

        # (15 - 5) * 10
        self.assertEqual(quant1['value'], 100.0)
        # (10 - 5) * 10
        self.assertEqual(quant2['value'], 50.0)

    def test_cost_method_fifo(self):
        self.product1.categ_id.property_cost_method = 'fifo'

        # receive 15 units @ 10 in location 1
        move1 = self.env['stock.move'].create({
            'name': 'Receive 15 units at 10',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location1.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 15.0,
            'price_unit': 10,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done = 15.0
        move1._action_done()

        # receive 10 units @ 15 in location 2
        move2 = self.env['stock.move'].create({
            'name': 'Receive 10 units at 15',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location2.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 10.0,
            'price_unit': 15,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids.qty_done = 10.0
        move2._action_done()

        # sell 5 units of location 1
        move3 = self.env['stock.move'].create({
            'name': 'Deliver 5 units',
            'location_id': self.stock_location1.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 5.0,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids.qty_done = 5.0
        move3._action_done()

        # sell 5 units of location 2
        move4 = self.env['stock.move'].create({
            'name': 'Deliver 5 units',
            'location_id': self.stock_location2.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 5.0,
        })
        move4._action_confirm()
        move4._action_assign()
        move4.move_line_ids.qty_done = 5.0
        move4._action_done()

        quant1 = self.env['stock.quant'].read_group([
            ('product_id', '=', self.product1.id),
            ('location_id', '=', self.stock_location1.id)],
            ['value'], ['location_id'])[0]
        quant2 = self.env['stock.quant'].read_group([
            ('product_id', '=', self.product1.id),
            ('location_id', '=', self.stock_location2.id)],
            ['value'], ['location_id'])[0]

        # 200 / 15 * 10
        self.assertEqual(quant1['value'], 133.33)
        # 200 / 15 * 5
        self.assertEqual(quant2['value'], 66.67)
