# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestQuotedQty(TransactionCase):
    """Test the computation of the quoted quantity"""

    def setUp(self):
        super(TestQuotedQty, self).setUp()

        #  Get a product
        self.product = self.browse_ref('product.product_product_10')
        # Create a new variant of the same template
        self.product2 = self.env['product.product'].create(
            {'name': 'New variant',
             'standard_price': 1,
             'type': 'product',
             'uom_id': self.ref('product.product_uom_unit'),
             'default_code': 'NEW',
             'product_tmpl_id': self.product.product_tmpl_id.id})

        # Cancel all the previous Quotations
        all_variants = self.product.product_tmpl_id.product_variant_ids
        lines = self.env['sale.order.line'].search(
            [('product_id', 'in', all_variants.ids),
             ('state', '=', 'draft')])
        orders = lines.mapped(lambda l: l.order_id)
        orders.action_cancel()

        #  Record the initial quantity available for sale
        self.initial_usable_qty = self.product.immediately_usable_qty

        # Get the warehouses
        self.wh_main = self.browse_ref('stock.warehouse0')
        self.wh_ch = self.browse_ref('stock.stock_warehouse_shop0')

        #  Create a UoM in the category of PCE
        self.thousand = self.env['product.uom'].create({
            'name': 'Thousand',
            'factor': 0.001,
            'rounding': 0.00,
            'uom_type': 'bigger',
            'category_id': self.ref('product.product_uom_categ_unit')})

    def assertImmediatelyUsableQty(self, record, qty, msg):
        record.refresh()
        self.assertEqual(
            record.immediately_usable_qty - self.initial_usable_qty, qty, msg)

    def assertQuotedQty(self, record, qty, msg):
        record.refresh()
        self.assertEqual(
            record.quoted_qty, qty, msg)

    def test_quoted_qty(self):

        def assertQuotedQty(record, qty, msg):
            self.assertEqual(
                record.quoted_qty, qty, msg)

        # The quoted quantity should be 0
        self.assertQuotedQty(
            self.product, 0.0, "Check initial quoted quantity")

        # Enter a Quotation
        order1 = self.env['sale.order'].create({
            'partner_id': self.ref('base.res_partner_2'),
            'partner_invoice_id': self.ref('base.res_partner_address_8'),
            'partner_shipping_id': self.ref('base.res_partner_address_8'),
            'pricelist_id': self.ref('product.list0'),
            'warehouse_id': self.wh_main.id})
        self.env['sale.order.line'].create({
            'order_id': order1.id,
            'name': 'Quotation line 1',
            'product_uom': self.ref('product.product_uom_unit'),
            'product_uom_qty': 107.0,
            'state': 'draft',
            'product_id': self.product.id})
        #  Check the qty available for sale
        self.assertImmediatelyUsableQty(
            self.product, -107.0, "Check the quantity available for sale")
        # Check by variant/template
        self.assertQuotedQty(
            self.product, 107.0, "Check quoted quantity for first variant")
        self.assertQuotedQty(
            self.product2, 0.0, "Check quoted quantity for second variant")
        self.assertQuotedQty(
            self.product.product_tmpl_id, 107.0,
            "Check quoted quantity for template")
        # Check by warehouse
        self.assertQuotedQty(
            self.product.with_context(warehouse=self.wh_main.id), 107.0,
            "Check quoted quantity in main WH")
        self.assertQuotedQty(
            self.product.with_context(warehouse=self.wh_ch.id), 0.0,
            "Check quoted quantity in Chicago WH")
        # Check by location
        self.assertQuotedQty(
            self.product.with_context(
                location=self.wh_main.lot_stock_id.id), 107.0,
            "Check quoted quantity in main WH location")
        self.assertQuotedQty(
            self.product.with_context(
                location=self.wh_ch.lot_stock_id.id),
            0.0,
            "Check quoted quantity in Chicago WH location")

        # Enter another Quotation
        order2 = self.env['sale.order'].create({
            'partner_id': self.ref('base.res_partner_2'),
            'partner_invoice_id': self.ref('base.res_partner_address_9'),
            'partner_shipping_id': self.ref('base.res_partner_address_9'),
            'pricelist_id': self.ref('product.list0'),
            'warehouse_id': self.wh_ch.id})
        self.env['sale.order.line'].create({
            'order_id': order2.id,
            'name': 'Quotation 2',
            'product_uom': self.thousand.id,
            'product_uom_qty': 0.613,
            'state': 'draft',
            'product_id': self.product.id})
        #  Check the qty available for sale
        self.assertImmediatelyUsableQty(
            self.product, -720.0, "Check the quantity available for sale")
        # Check by variant/template
        self.assertQuotedQty(
            self.product, 720.0, "Check quoted quantity for first variant")
        self.assertQuotedQty(
            self.product2, 0.0, "Check quoted quantity for second variant")
        self.assertQuotedQty(
            self.product.product_tmpl_id, 720.0,
            "Check quoted quantity for template")
        # Check by warehouse
        self.assertQuotedQty(
            self.product.with_context(warehouse=self.wh_main.id), 107.0,
            "Check quoted quantity in main WH")
        self.assertQuotedQty(
            self.product.with_context(warehouse=self.wh_ch.id), 613.0,
            "Check quoted quantity in Chicago WH")
        # Check by location
        self.assertQuotedQty(
            self.product.with_context(
                location=self.wh_main.lot_stock_id.id), 107.0,
            "Check quoted quantity in main WH location")
        self.assertQuotedQty(
            self.product.with_context(
                location=self.wh_ch.lot_stock_id.id), 613.0,
            "Check quoted quantity in Chicago WH location")

        # Add a line for the other variant
        self.env['sale.order.line'].create({
            'order_id': order2.id,
            'name': 'Quotation line 2',
            'product_uom': self.ref('product.product_uom_unit'),
            'product_uom_qty': 22.0,
            'state': 'draft',
            'product_id': self.product2.id})
        # Check by variant/template
        self.assertQuotedQty(
            self.product, 720.0,
            "Check quoted quantity for first variant")
        self.assertQuotedQty(
            self.product2, 22.0,
            "Check quoted quantity for second variant")
        self.assertQuotedQty(
            self.product.product_tmpl_id, 742.0,
            "Check quoted quantity for template")

        # Confirm one of the Quotations
        order1.signal_workflow('order_confirm')
        # Check qty avl. for sale (unchanged: quotation turned into delivery)
        self.assertImmediatelyUsableQty(
            self.product, -720.0, "Check the quantity available for sale")
        # Check by variant
        self.assertQuotedQty(
            self.product, 613.0,
            "Check quoted quantity for first variant")
        self.assertQuotedQty(
            self.product2, 22.0,
            "Check quoted quantity for second variant")
        self.assertQuotedQty(
            self.product.product_tmpl_id, 635.0,
            "Check quoted quantity for template")
        # Check by warehouse
        self.assertQuotedQty(
            self.product.with_context(warehouse=self.wh_main.id), 0.0,
            "Check quoted quantity in main WH")
        self.assertQuotedQty(
            self.product.with_context(warehouse=self.wh_ch.id), 613.0,
            "Check quoted quantity in Chicago WH")
        # Check by location
        self.assertQuotedQty(
            self.product.with_context(
                location=self.wh_main.lot_stock_id.id), 0.0,
            "Check quoted quantity in main WH location")
        self.assertQuotedQty(
            self.product.with_context(
                location=self.wh_ch.lot_stock_id.id), 613.0,
            "Check quoted quantity in Chicago WH location")
