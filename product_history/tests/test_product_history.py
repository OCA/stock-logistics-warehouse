#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductHistory(TransactionCase):

    def setUp(self):
        super(TestProductHistory, self).setUp()
        self.product = self.env['product.product'].create(
            {'name': 'Test Product', 'type': 'product'})
        self.stock_location_id = self.env.ref('stock.stock_location_stock').id
        self.customer_location_id = self.env.ref(
            'stock.stock_location_customers').id
        self.supplier_location_id = self.env.ref(
            'stock.stock_location_suppliers').id
        self.loss_location_id = self.env.ref(
            'stock.stock_location_scrapped').id
        # Purchase moves
        for product_qty in [5, 5, 10]:
            self.move = self.env['stock.move'].create({
                'product_id': self.product.id,
                'name': 'Test In',
                'product_uom_qty': product_qty,
                'quantity_done': product_qty,
                'product_uom': self.product.uom_id.id,
                'location_id': self.supplier_location_id,
                'location_dest_id': self.stock_location_id,
            })
            self.move._action_done()
            self.move.date = '2019-12-01'
        # Sales Moves
        for product_qty in [2, 5]:
            self.move = self.env['stock.move'].create({
                'product_id': self.product.id,
                'name': 'Test Out',
                'product_uom_qty': product_qty,
                'quantity_done': product_qty,
                'product_uom': self.product.uom_id.id,
                'location_id': self.stock_location_id,
                'location_dest_id': self.customer_location_id,
            })
            self.move._action_done()
            self.move.date = '2019-12-21'
        # Loss Move
        self.move_loss = self.env['stock.move'].create({
            'product_id': self.product.id,
            'name': 'Test Loss',
            'product_uom_qty': 3,
            'quantity_done': 3,
            'product_uom': self.product.uom_id.id,
            'location_id': self.stock_location_id,
            'location_dest_id': self.loss_location_id,
        })
        self.move_loss._action_done()
        self.move_loss.date = '2020-01-01'

    def test_001_compute_weeks_history(self):
        self.product.history_range = 'weeks'
        self.env['product.product'].job_compute_history(
            'weeks', [self.product.id])
        self.assertEquals(self.product.product_history_ids[-1].end_qty, 20.0,
                          "Purchase Quantity of a product should be 20.0")
        self.assertEquals(self.product.product_history_ids[-1].purchase_qty,
                          20.0,
                          "End Quantity of a product should be 20.0")
        self.assertEquals(self.product.product_history_ids[-1].sale_qty, 0.0,
                          "Sale Quantity of a product should be 0.0")
        self.assertEquals(self.product.product_history_ids[-4].sale_qty, -7.0,
                          "Sale Quantity of a product should be -7.0")
        self.assertEquals(self.product.product_history_ids[-6].loss_qty, -3.0,
                          "Loss Quantity of a product should be -3.0")
        self.assertEquals(self.product.product_history_ids[0].end_qty, 10.0,
                          "Purchase Quantity of a product should be 10.0")

    def test_002_compute_months_history(self):
        self.product.history_range = 'months'
        self.env['product.product'].job_compute_history(
            'months', [self.product.id])
        self.assertEquals(self.product.product_history_ids[-1].end_qty, 13.0,
                          "Purchase Quantity of a product should be 13.0")
        self.assertEquals(self.product.product_history_ids[-1].purchase_qty,
                          20.0,
                          "End Quantity of a product should be 20.0")
        self.assertEquals(self.product.product_history_ids[-1].sale_qty, -7.0,
                          "Sale Quantity of a product should be -7.0")
