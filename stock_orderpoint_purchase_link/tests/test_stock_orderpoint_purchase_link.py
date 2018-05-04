# Copyright 2018 Open Source Integrators
#   (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockOrderpointPurchaseLink(common.TransactionCase):

    def setUp(self):
        super(TestStockOrderpointPurchaseLink, self).setUp()

        # Refs
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.route_buy = self.warehouse.buy_pull_id.route_id.id
        self.route_mto = self.warehouse.mto_pull_id.route_id.id

        # Get required Model
        self.product_model = self.env['product.product']
        self.purchase_line_model = self.env['purchase.order.line']
        self.stock_move_model = self.env['stock.move']
        self.orderpoint_model = self.env['stock.warehouse.orderpoint']

        # Create Supplier, Products, Orderpoint
        self.supplier = self._create_supplier()
        self.product = self._create_product()
        self.orderpoint = self._create_orderpoint()

    def _create_supplier(self):
        supplier = self.env['res.partner'].create({
            'name': 'OSI',
            'is_company': True,
            'supplier': True
        })
        return supplier

    def _create_product(self):
        """Create a Product."""
        product = self.product_model.create({
            'name': 'OSI MTS',
            'standard_price': 1,
            'type': 'product',
            'uom_id': self.product_uom.id,
            'route_ids': [(6, 0, [self.route_buy, self.route_mto])],
            'seller_ids': [(0, False, {'name': self.supplier.id, 'delay': 1})]
        })
        return product

    def _create_orderpoint(self):
        """Create a Orderpoint."""
        orderpoint = self.orderpoint_model.create({
            'warehouse_id': self.warehouse.id,
            'location_id': self.location_stock.id,
            'product_id': self.product.id,
            'product_max_qty': 24,
            'product_min_qty': 12,
            'product_uom': self.product_uom.id,
        })
        return orderpoint

    def test_stock_orderpoint_purchase_link(self):
        """Test stock orderpoint purchase link"""

        # Update warehouse configuration for incoming shipments one step
        self.warehouse.write({'reception_steps': 'one_step'})
        # Run scheduler
        self.env['procurement.group'].run_scheduler()
        # Check purchase order line match with orderpoint
        purchase_line_1 = self.purchase_line_model.search(
            [('orderpoint_id', '=', self.orderpoint.id)])
        self.assertEqual(len(purchase_line_1), 1)
        # Cancel purchase order and delete it
        purchase_line_1.order_id.button_cancel()
        purchase_line_1.order_id.unlink()
        # Cancel stock move and unlink it
        move_line = self.stock_move_model.search(
            [('product_id', '=', self.product.id)])
        move_line._action_cancel()
        move_line.unlink()
        # Update warehouse configuration for incoming shipments two steps
        self.warehouse.write({'reception_steps': 'two_steps'})
        # Run scheduler
        self.env['procurement.group'].run_scheduler()
        # Check purchase order line match with orderpoint
        purchase_line_2 = self.purchase_line_model.search(
            [('orderpoint_id', '=', self.orderpoint.id)])
        self.assertEqual(len(purchase_line_2), 1)
        # Unlink purchase order
        purchase_line_2.order_id.button_cancel()
        purchase_line_2.order_id.unlink()
        # Cancel stock move and unlink it
        move_line = self.stock_move_model.search(
            [('product_id', '=', self.product.id)])
        move_line._action_cancel()
        move_line.unlink()
        # Update warehouse configuration for incoming shipments three steps
        self.warehouse.write({'reception_steps': 'three_steps'})
        # Run scheduler
        self.env['procurement.group'].run_scheduler()
        # Check purchase order line match with orderpoint
        purchase_line_3 = self.purchase_line_model.search(
            [('orderpoint_id', '=', self.orderpoint.id)])
        self.assertEqual(len(purchase_line_3), 1)
        # Unlink purchase order
        purchase_line_3.order_id.button_cancel()
        purchase_line_3.order_id.unlink()
        # Cancel stock move and unlink it
        move_line = self.stock_move_model.search(
            [('product_id', '=', self.product.id)])
        move_line._action_cancel()
        move_line.unlink()
