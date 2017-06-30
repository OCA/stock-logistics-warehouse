# -*- coding: utf-8 -*-

from datetime import datetime
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestOnchangeProductId(TransactionCase):

    def setUp(self):
        super(TestOnchangeProductId, self).setUp()
        self.fiscal_position_model = self.env['account.fiscal.position']
        self.fiscal_position_tax_model = self.env[
            'account.fiscal.position.tax']
        self.tax_model = self.env['account.tax']
        self.po_model = self.env['purchase.order']
        self.po_line_model = self.env['purchase.order.line']
        self.res_partner_model = self.env['res.partner']
        self.product_tmpl_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.product_uom_model = self.env['product.uom']
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.stock_location_model = self.env['stock.location']
        self.product_pricelist_model = self.env['product.pricelist']

    def test_onchange_product_purchase_line(self):
        # get uom
        uom_id = self.product_uom_model.search([('name', '=', 'Unit(s)')])[0]

        # create a partner
        partner_id = self.res_partner_model.create(dict(name="Testpartner"))

        # create a fiscal position

        fp_id = self.fiscal_position_model.create(
            {'name': "fiscal position", 'sequence': 1}
        )

        # taxes

        tax_include_id = self.tax_model.create({'name': "Include tax",
                                                'amount': '21.00',
                                                'price_include': True,
                                                'type_tax_use': 'purchase'})

        # create tmpl and product

        category_per30 = self.env.ref(
            'stock_reorder_forecast.cat_period_30')
        product_tmpl_id = self.product_tmpl_model.create(
            {'name': "TESTPRDTMPL",
             'list_price': 88,
             'supplier_taxes_id': [(6, 0, [tax_include_id.id])],
             'categ_id': category_per30.id, }
        )

        supplier_new = self.supplierinfo_model.create({
            'name': partner_id.id,
            'product_tmpl_id': product_tmpl_id.id,
        })
        product_id = self.product_model.create(
            {'product_tmpl_id': product_tmpl_id.id,
             'seller_ids': [(6, 0, [supplier_new.id])], }
        )
        stock_location_id = self.stock_location_model.search(
            [], limit=1)
        pricelist_id = self.product_pricelist_model.search(
            [], limit=1)
        # supplier
        # create a purchase order, quantity 0.0 to trigger main branch of
        # onchange method
        purchase_order = self.po_model.create({
            'partner_id': partner_id.id,
            'location_id': stock_location_id.id,
            'pricelist_id': pricelist_id.id,
            'name': 'TESTPOTMPL',
            'invoice_method': 'manual',
        })
        orderline = self.po_line_model.create(
            {'order_id': purchase_order.id,
             'name': product_id.name,
             'product_id': product_id.id,
             'product_qty': 0.0,
             'product_uom': uom_id.id,
             'price_unit': 121.0,
             'date_planned': datetime.today().strftime(
                 DEFAULT_SERVER_DATETIME_FORMAT), }
        )
        self.assertEqual(
            1.0, orderline._get_purchase_multiple()
        )
        supplier_new.write({'purchase_multiple': 3.0})
        self.assertEqual(
            3.0, orderline._get_purchase_multiple()
        )
        self.assertEqual(
            185, orderline._get_stock_period_max()
        )
        category_per30.write({'stock_period_max': 55})
        self.assertEqual(
            55, orderline._get_stock_period_max()
        )
        partner_id.write({'stock_period_max': 43})
        self.assertEqual(
            43, orderline._get_stock_period_max()
        )
        product_id.write({'stock_period_max': 3})
        self.assertEqual(
            3, orderline._get_stock_period_max()
        )
        orderline.onchange_product_id(
            pricelist_id.id, product_id.id,
            orderline.product_qty, uom_id.id, partner_id.id)
        self.assertEqual(1.0, orderline.product_qty)
