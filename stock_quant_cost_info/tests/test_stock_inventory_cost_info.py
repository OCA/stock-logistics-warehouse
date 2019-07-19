# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockInventoryCostInfo(TransactionCase):
    def setUp(self):
        super(TestStockInventoryCostInfo, self).setUp()
        product_obj = self.env['product.product']
        self.product_1 = product_obj.create({
            'name': 'product test 1',
            'type': 'product',
            'standard_price': 1000,
        })
        self.product_2 = product_obj.create({
            'name': 'product test 2',
            'type': 'product',
            'standard_price': 2000,
        })
        # Initial inventory: set quantities to zero
        initial_inventory = self.env['stock.inventory'].create({
            'name': 'Initial inventory',
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': self.product_1.id,
                'location_id': self.env.ref('stock.warehouse0').lot_stock_id.id
            }), (0, 0, {
                'product_id': self.product_2.id,
                'location_id': self.env.ref('stock.warehouse0').lot_stock_id.id
            })]
        })
        initial_inventory.action_reset_product_qty()
        initial_inventory.action_done()
        # Another inventory adjustment
        self.inventory = self.env['stock.inventory'].create({
            'name': 'Another inventory',
            'filter': 'partial',
        })
        initial_inventory.action_start()
        self.inventory.write({
            'line_ids': [(0, 0, {
                'product_id': self.product_1.id,
                'product_qty': 10,
                'location_id': self.env.ref('stock.warehouse0').lot_stock_id.id
            }), (0, 0, {
                'product_id': self.product_2.id,
                'product_qty': 20,
                'location_id': self.env.ref('stock.warehouse0').lot_stock_id.id
            })]
        })

    def test_compute_adjustment_cost(self):
        """Tests if the adjustment_cost is correctly computed."""
        lines = self.inventory.line_ids
        line = lines.filtered(lambda r: r.product_id == self.product_1)
        self.assertEqual(line.adjustment_cost, 10000)
        line = lines.filtered(lambda r: r.product_id == self.product_2)
        self.assertEqual(line.adjustment_cost, 40000)
        # check the adjustment cost after validate the inventory
        self.product_1.standard_price = 10000
        self.product_2.standard_price = 20000
        self.inventory.action_done()
        line = lines.filtered(lambda r: r.product_id == self.product_1)
        self.assertEqual(line.adjustment_cost, 100000)
        line = lines.filtered(lambda r: r.product_id == self.product_2)
        self.assertEqual(line.adjustment_cost, 400000)
