# Copyright 2014 Numérigraphe SARL
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestQuotedQty(common.SavepointCase):
    """Test the computation of the quoted quantity"""

    @classmethod
    def setUpClass(cls):
        super(TestQuotedQty, cls).setUpClass()
        cls.product_tmpl = cls.env['product.template'].create({
            'name': 'Test product template',
        })
        cls.uom_cat = cls.env['uom.category'].create({
            'name': 'Coolness',
        })
        cls.uom = cls.env['uom.uom'].create({
            'name': 'odoos',
            'category_id': cls.uom_cat.id,
        })
        cls.product1 = cls.env['product.product'].create({
            'name': 'Test variant 1',
            'standard_price': 1.0,
            'type': 'product',
            'uom_id': cls.uom.id,
            'uom_po_id': cls.uom.id,
            'default_code': 'V01',
            'product_tmpl_id': cls.product_tmpl.id,
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'Test variant 2',
            'standard_price': 1.0,
            'type': 'product',
            'uom_id': cls.uom.id,
            'uom_po_id': cls.uom.id,
            'default_code': 'V02',
            'product_tmpl_id': cls.product_tmpl.id,
        })
        cls.wh_main = cls.env['stock.warehouse'].create({
            'name': 'Main Test Warehouse',
            'code': 'MTESTW'
        })
        cls.wh_shop = cls.env['stock.warehouse'].create({
            'name': 'Secondary Test Warehouse',
            'code': 'STESTW',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
        })
        #  Record the initial quantity available for sale
        cls.initial_usable_qty = cls.product1.immediately_usable_qty
        #  Create a UoM in the category of PCE
        cls.thousand = cls.env['uom.uom'].create({
            'name': 'Thousand',
            'factor': 0.001,
            'rounding': 0.001,
            'uom_type': 'bigger',
            'category_id': cls.uom_cat.id,
        })

    def assertinmediatelyusableqty(self, record, qty, msg):
        record.refresh()
        self.assertEqual(
            record.immediately_usable_qty - self.initial_usable_qty, qty, msg)

    def assertquotedqty(self, record, qty, msg):
        record.refresh()
        self.assertEqual(
            record.quoted_qty, qty, msg)

    def test_quoted_qty(self):
        # The quoted quantity should be 0
        self.assertquotedqty(
            self.product1, 0.0, "Check initial quoted quantity")
        # Enter a Quotation
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'warehouse_id': self.wh_main.id,
            'order_line': [(0, 0, {
                'product_id': self.product1.id,
                'name': 'Quotation line 1',
                'product_uom': self.uom.id,
                'product_uom_qty': 107.0,
                'state': 'draft',
            })],
        })
        #  Check the qty available for sale
        self.assertinmediatelyusableqty(
            self.product1, -107.0,
            "Check the quantity of variant available for sale")
        self.assertinmediatelyusableqty(
            self.product1.product_tmpl_id, -107.0,
            "Check the quantity of product available for sale")
        # Check by variant/template
        self.assertquotedqty(
            self.product1, 107.0, "Check quoted quantity for first variant")
        self.assertquotedqty(
            self.product2, 0.0, "Check quoted quantity for second variant")
        self.assertquotedqty(
            self.product1.product_tmpl_id, 107.0,
            "Check quoted quantity for template")
        # Check by warehouse
        self.assertquotedqty(
            self.product1.with_context(warehouse=self.wh_main.id), 107.0,
            "Check quoted quantity in main WH")
        self.assertquotedqty(
            self.product1.with_context(warehouse=self.wh_shop.id), 0.0,
            "Check quoted quantity in Chicago WH")
        # Check by location
        self.assertquotedqty(
            self.product1.with_context(
                location=self.wh_main.lot_stock_id.id), 107.0,
            "Check quoted quantity in main WH location")
        self.assertquotedqty(
            self.product1.with_context(
                location=self.wh_shop.lot_stock_id.id),
            0.0,
            "Check quoted quantity in Chicago WH location")
        # Enter another Quotation
        order2 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'warehouse_id': self.wh_shop.id,
            'order_line': [(0, 0, {
                'product_id': self.product1.id,
                'name': 'Quotation 2',
                'product_uom': self.thousand.id,
                'product_uom_qty': 0.613,
                'state': 'draft',
            })],
        })
        #  Check the qty available for sale
        self.assertinmediatelyusableqty(
            self.product1, -720.0, "Check the quantity available for sale")
        # Check by variant/template
        self.assertquotedqty(
            self.product1, 720.0, "Check quoted quantity for first variant")
        self.assertquotedqty(
            self.product2, 0.0, "Check quoted quantity for second variant")
        self.assertquotedqty(
            self.product1.product_tmpl_id, 720.0,
            "Check quoted quantity for template")
        # Check by warehouse
        self.assertquotedqty(
            self.product1.with_context(warehouse=self.wh_main.id), 107.0,
            "Check quoted quantity in main WH")
        self.assertquotedqty(
            self.product1.with_context(warehouse=self.wh_shop.id), 613.0,
            "Check quoted quantity in shop WH")
        # Check by location
        self.assertquotedqty(
            self.product1.with_context(
                location=self.wh_main.lot_stock_id.id), 107.0,
            "Check quoted quantity in main WH location")
        self.assertquotedqty(
            self.product1.with_context(
                location=self.wh_shop.lot_stock_id.id), 613.0,
            "Check quoted quantity in shop WH location")
        # Add a line for the other variant
        self.env['sale.order.line'].create({
            'order_id': order2.id,
            'name': 'Quotation line 2',
            'product_uom': self.uom.id,
            'product_uom_qty': 22.0,
            'state': 'draft',
            'product_id': self.product2.id})
        # Check by variant/template
        self.assertquotedqty(
            self.product1, 720.0,
            "Check quoted quantity for first variant")
        self.assertquotedqty(
            self.product2, 22.0,
            "Check quoted quantity for second variant")
        self.assertquotedqty(
            self.product1.product_tmpl_id, 742.0,
            "Check quoted quantity for template")
        # Confirm one of the Quotations
        order1.action_confirm()
        # Check qty avl. for sale (unchanged: quotation turned into delivery)
        self.assertinmediatelyusableqty(
            self.product1, -720.0, "Check the quantity available for sale")
        # Check by variant
        self.assertquotedqty(
            self.product1, 613.0,
            "Check quoted quantity for first variant")
        self.assertquotedqty(
            self.product2, 22.0,
            "Check quoted quantity for second variant")
        self.assertquotedqty(
            self.product1.product_tmpl_id, 635.0,
            "Check quoted quantity for template")
        # Check by warehouse
        self.assertquotedqty(
            self.product1.with_context(warehouse=self.wh_main.id), 0.0,
            "Check quoted quantity in main WH")
        self.assertquotedqty(
            self.product1.with_context(warehouse=self.wh_shop.id), 613.0,
            "Check quoted quantity in shop WH")
        # Check by location
        self.assertquotedqty(
            self.product1.with_context(
                location=self.wh_main.lot_stock_id.id), 0.0,
            "Check quoted quantity in main WH location")
        self.assertquotedqty(
            self.product1.with_context(
                location=self.wh_shop.lot_stock_id.id), 613.0,
            "Check quoted quantity in shop WH location")
