
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, timedelta

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tests.common import TransactionCase


class TestWizards(TransactionCase):

    def setUp(self):
        super(TestWizards, self).setUp()
        self.model_data_obj = self.env['ir.model.data']
        self.product_obj = self.env['product.product']
        self.sale_order_obj = self.env['sale.order']
        self.partner_agrolite_id = self.model_data_obj.xmlid_to_res_id(
            'base.res_partner_2'
        )
        self.supplier3 = self.env.ref(
            'stock_reorder_forecast.product_supplierinfo_3'
        )
        self.product_period180 = self.env.ref(
            'stock_reorder_forecast.product_period180')

    def test_wizards(self):
        # check calcultation of ultimate date
        # Verify PO creation  (correct date and correct stock)
        so1 = self.sale_order_obj.create({
            'partner_id': self.partner_agrolite_id,
            'partner_invoice_id': self.partner_agrolite_id,
            'partner_shipping_id': self.partner_agrolite_id,
            'order_line': [(0, 0, {
                'name': self.product_period180.name,
                'product_id': self.product_period180.id,
                'product_uom_qty': 184,
                'product_uom': self.product_period180.uom_id.id,
                'price_unit': 75})],
            'pricelist_id': self.env.ref('product.list0').id, })
        dateplanned = (date.today() + timedelta(days=0)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        self.assertEqual(False, self.product_period180.has_purchase_draft())
        # Wizard note:  ultimate_purchase_to will be date planned
        self.supplier3.name.write({
            'stock_period_min': 12, 'stock_period_max': 89})

        self.product_obj.calc_purchase_date()
        self.assertEqual(False, self.product_period180.ultimate_purchase)
        wiz_dict = {
            'product': self.product_period180.id,
            'supplier': self.supplier3.id,
            'name': self.supplier3.name,
            'stock_period_min': self.supplier3.name.stock_period_min,
            'stock_period_max': self.supplier3.name.stock_period_max,
            'ultimate_purchase_to': dateplanned,
        }
        tstwiz = self.env['purchase.purchase_wizard'].create(wiz_dict)
        self.assertEqual(False, self.product_period180.has_purchase_draft())
        purchase = tstwiz.create_rfq()
        # will still be false because we did not update average
        self.assertEqual(False, self.product_period180.has_purchase_draft())
        # Recalculate params and relaunch the wizard
        self.product_obj.calc_purchase_date()
        self.assertEqual(False, self.product_period180.ultimate_purchase)
        purchase = tstwiz.create_rfq()
        # Still false because no sale confirmed and therefore average still 0
        self.assertEqual(False, self.product_period180.has_purchase_draft())
        self.assertEqual(False, self.product_period180.ultimate_purchase)
        res = tstwiz.with_context(
            active_ids=self.product_period180.ids).default_get([])
        self.assertEqual(False, res['ultimate_purchase'])
        self.assertEqual(0.0, res['stock_avl'])
        # product ultimate purchase should be false now,
        so1.action_confirm()
        self.product_obj.calc_purchase_date()
        # testing update_proposal
        self.assertEqual(
            False,
            self.product_period180.ultimate_purchase
        )
        self.assertEqual(True, self.product_period180.has_purchase_draft())
        purchase = tstwiz.create_rfq()
        # verify PO date and PO quantity
        self.assertEqual(1, len(purchase))
        self.assertEqual(False, self.product_period180.ultimate_purchase)
        self.assertEqual(
            tstwiz._get_qty(self.product_period180, self.supplier3,
                            self.supplier3.name.stock_period_max),
            purchase.order_line[0].product_qty
        )
        partner = self.supplier3.name
        wiz_primary_dict = {
            'product': self.product_period180.id,
            'supplier': self.supplier3.id,
            'name': partner.id,
            'stock_period_min': self.supplier3.name.stock_period_min,
            'stock_period_max': self.supplier3.name.stock_period_max,
            'ultimate_purchase_to': dateplanned,
            'primary_supplier_only': False,
        }
        tst_primary_wiz = self.env['purchase.purchase_supplier_wizard'].create(
            wiz_primary_dict
        )
        self.product_obj.calc_purchase_date()
        purchase = tst_primary_wiz.create_partner_rfq()
        # the wizard is called with an active id of res.partner
        res = tst_primary_wiz.with_context(
            active_ids=[partner.id]).default_get([])
        self.assertEqual(
            False,
            res['ultimate_purchase'])
        # testing update_proposal
        self.assertEqual(
            False,
            partner.ultimate_purchase)
