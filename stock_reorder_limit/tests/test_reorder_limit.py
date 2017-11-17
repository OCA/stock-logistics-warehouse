# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp.tests.common import TransactionCase


_logger = logging.getLogger(__name__)


class TestReorderLimit(TransactionCase):
    """Test limits on automatic procurement for minimum stock rules.

    We will create a stockable product that we van buy/purchase.
    Then we create a minimum stock rule that the product should be ordered,
    when less then 5 in stock. maximum will be 15, and we will order in
    multiples of 5.

    Test 1 is to run the scheduler with minimum stock rules. There is no
    stock, so 15 products should be procured.

    After processing (approving purchase and receiving goods) virtual
    available stock should be 15.

    We sell 12 pieces (virtual available back to 3) and then make the
    product obsolete. Next procurement should procure no products.

    We sell another 10 product (virtual available back to -7). Next
    procurement should be for 10 products, because must still be multiple of 5.

    We sell another 10 products (virtual available again back to -7) and
    disable the purchase_ok flag. Next procurement should not procure any
    products.
    """
    def _print_procurement_messages(self, procurement):
        """If anything goes wrong in test, it would be nice to know what."""
        _logger.info("Messages for procurement %s:" % procurement.name)
        messages = self.env['mail.message'].search(
            [('model', '=', 'procurement.order'),
             ('res_id', '=', procurement.id)],
            order='create_date')
        for message in messages:
            _logger.info(message.body)

    def _procure_product(self, warehouse, product, expected_quantity):
        """Procure product and return procurement order."""
        procurement_model = self.env['procurement.order']
        # Make sure all previous procurements have completed:
        running_procurements = procurement_model.search(
            [('product_id', '=', product.id),
             ('warehouse_id', '=', warehouse.id)])
        for procurement in running_procurements:
            for move in procurement.move_ids:
                move.action_done()
            self.assertEqual(procurement.state, 'done')
        procurement_model.run_scheduler()
        procurement = procurement_model.search(
            [('product_id', '=', product.id),
             ('warehouse_id', '=', warehouse.id)],
            order='id desc',  # create_date might not be unique
            limit=1)
        if expected_quantity == 0.0:
            if procurement and procurement.state == 'running':
                self._print_procurement_messages(procurement)
                self.assertNotEqual(procurement.state, 'running')
            return
        self.assertTrue(len(procurement) == 1)
        if procurement.state != 'running':
            self._print_procurement_messages(procurement)
        self.assertEqual(procurement.state, 'running')
        self.assertEqual(procurement.product_qty, expected_quantity)
        po = procurement.purchase_line_id.order_id
        po.signal_workflow('purchase_confirm')
        self.assertEqual(po.state, 'approved')

    def _sell_product(self, customer, warehouse, product, uom, quantity):
        """Sell product, to bring quantity available down."""
        sale_order_model = self.env['sale.order']
        sale_line_model = self.env['sale.order.line']
        sale_order = sale_order_model.create({
            'partner_id': customer.id,
            'warehouse_id': warehouse.id,
            'state': 'draft'})
        sale_line_model.create({
            'order_id': sale_order.id,
            'name': 'Enjoy your product',
            'product_uom': uom.id,
            'product_uom_qty': quantity,
            'state': 'draft',
            'product_id': product.id})
        sale_order.signal_workflow('order_confirm')

    def test_reorder_limit(self):
        # Create basic test data:
        data_model = self.env['ir.model.data']
        categ_unit = data_model.xmlid_to_res_id(
            'product.product_uom_categ_unit')
        uom_model = self.env['product.uom']
        uom_unit = uom_model.create({
            'name': 'Test-Unit',
            'category_id': categ_unit,
            'factor': 1,
            'uom_type': 'reference',
            'rounding': 1.0})
        partner_model = self.env['res.partner']
        our_customer = partner_model.create({
            'name': 'Our good customer',
            'customer': True})
        our_supplier = partner_model.create({
            'name': 'Our friendly supplier',
            'supplier': True})
        product_model = self.env['product.product']
        our_product = product_model.create({
            'name': 'Our nice little product',
            'purchase_ok': True,
            'type': 'product',
            'seller_ids': [
                (0, False, {
                    'name': our_supplier.id,
                    'delay': 1,
                    'min_qty': 5})]})
        warehouse_model = self.env['stock.warehouse']
        our_warehouse = warehouse_model.create({
            'name': 'Our warehouse',
            'code': 'ourwh'})
        orderpoint_model = self.env['stock.warehouse.orderpoint']
        orderpoint = orderpoint_model.create({
            'warehouse_id': our_warehouse.id,
            'location_id': our_warehouse.lot_stock_id.id,
            'product_id': our_product.id,
            'product_min_qty': 5,
            'product_max_qty': 15,
            'qty_multiple': 5,
            'product_uom': uom_unit.id})
        our_product_in_our_warehouse = our_product.with_context(
            location=our_warehouse.lot_stock_id.id)
        # Test 1: initial procurement
        orderpoint.write('name': 'Test 01')
        self.assertEqual(orderpoint.limit_procurement_qty, 15.0) 
        self._procure_product(our_warehouse, our_product, 15.0)
        self.assertEqual(
            our_product_in_our_warehouse.virtual_available, 15.0)
        # Test 2: sell 12 units and make product obsolete
        #     In this test we just move the products to an outside location:
        orderpoint.write('name': 'Test 02')
        self._sell_product(
            our_customer, our_warehouse, our_product, uom_unit, 12.0)
        self.assertEqual(
            our_product_in_our_warehouse.virtual_available, 3.0)
        our_product.write({'state': 'obsolete'})
        self.assertEqual(orderpoint.limit_procurement_qty, 5.0) 
        self._procure_product(our_warehouse, our_product, 0.0)
        # Test 3: sell another 10 units. Virtual available should go back
        #     to minus 7. Now procurement should acquire 10 units:
        orderpoint.write('name': 'Test 03')
        self._sell_product(
            our_customer, our_warehouse, our_product, uom_unit, 10.0)
        self.assertEqual(
            our_product_in_our_warehouse.virtual_available, -7.0)
        self._procure_product(our_warehouse, our_product, 10.0)
        self.assertEqual(
            our_product_in_our_warehouse.virtual_available, 3.0)
        # Test 4: Do not procure anything if purchase_ok is off:
        orderpoint.write('name': 'Test 04')
        our_product.write({'purchase_ok': False})
        self.assertEqual(orderpoint.limit_procurement_qty, 0.0) 
        self._sell_product(
            our_customer, our_warehouse, our_product, uom_unit, 10.0)
        self.assertEqual(
            our_product_in_our_warehouse.virtual_available, -7.0)
        self._procure_product(our_warehouse, our_product, 0.0)
        self.assertEqual(
            our_product_in_our_warehouse.virtual_available, -7.0)
