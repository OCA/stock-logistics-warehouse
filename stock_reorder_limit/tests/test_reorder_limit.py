# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
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

    def print_procurement_messages(self, procurement):
        """If anything goes wrong in test, it would be nice to know what."""
        messages = self.env['mail.message'].search(
            [('model', '=', 'procurement.order'),
             ('res_id', '=', procurement.id)],
            order='create_date'
        )
        for message in messages:
            _logger.info(message.body)

    def test_reorder_limit(self):
        # Create basic test data:
        data_model = self.env['ir.model.data']
        categ_unit = data_model.xmlid_to_res_id(
            'product.product_uom_categ_unit'
        )
        uom_model = self.env['product.uom']
        uom_unit = uom_model.create({
            'name': 'Test-Unit',
            'category_id': categ_unit,
            'factor': 1,
            'uom_type': 'reference',
            'rounding': 1.0,
        })
        partner_model = self.env['res.partner']
        our_supplier = partner_model.create({
            'name': 'Our friendly supplier',
            'supplier': True,
        })
        route_model = self.env['stock.location.route']
        buy_route = route_model.create({
            'name': 'buy',
            'sequence': 5,
            'product_selectable': True,
        })
        rule_model = self.env['procurement.rule']
        buy_rule = rule_model.create({
            'name': 'buy products for test',
            'action': 'buy',
            'procure_method': 'make_to_stock',
            'route_id': buy_route_id,

        })
        product_model = self.env['product.product']
        our_product = product_model.create({
            'name': 'Our nice little product',
            'purchase_ok': True,
            'type': 'product',
            'seller_ids': [
                (0, False, {
                    'name': our_supplier.id,
                    'delay': 1,
                    'min_qty': 5,
                })],
            'route_ids': [(4, buy_route.id)],
        })
        warehouse_model = self.env['stock.warehouse']
        our_warehouse = warehouse_model.create({
            'name': 'Our warehouse',
            'code': 'ourwh',
        })
        orderpoint_model = self.env['stock.warehouse.orderpoint']
        orderpoint_model.create({
            'warehouse_id': our_warehouse.id,
            'location_id': our_warehouse.lot_stock_id.id,
            'product_id': our_product.id,
            'product_min_qty': 5,
            'product_max_qty': 15,
            'qty_multiple': 5,
            'product_uom': uom_unit.id,
        })
        # Test 1: initial procurement
        procurement_model = self.env['procurement.order']
        procurement_model.run_scheduler()
        procurement = procurement_model.search(
            [('product_id', '=', our_product.id),
             ('warehouse_id', '=', our_warehouse.id)],
            order='create_date desc',
            limit=1
        )
        self.assertTrue(len(procurement) == 1)
        if procurement.state != 'running':
            self.print_procurement_messages(procurement)
        self.assertEqual(procurement.state, 'running')
        self.assertEqual(procurement.product_qty, 15.0)
        procurement.purchase_line_id.order_id.wkf_confirm_order()
        self.assertEqual(our_product.virtual_available, 15.0)
        # Test 2: sell 12 units amd make product obsolete
        #     In this test we just move the products to an outside location:
