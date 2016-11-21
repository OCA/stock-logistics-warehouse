
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, timedelta

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tests.common import TransactionCase


class TestWizards(TransactionCase):

    def setUp(self):
        super(TestWizards, self).setUp()
        self.supplier1 = self.env.ref(
            'stock_reorder_forecast.product_supplierinfo_1'
        )
        self.product_period90 = self.env.ref(
            'stock_reorder_forecast.product_period90')
        self.product_period180 = self.env.ref(
            'stock_reorder_forecast.product_period180')
        self.product_noper = self.env.ref(
            'stock_reorder_forecast.product_noper')


    def test_wizards(self):
        # check calcultation of ultimate date
        # Verify PO creation  (correct date and correct stock)
        # test wizard
        dateplanned = (date.today() + timedelta(days=200)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        # Wizard note:  ultimate_purchase_to will be date planned
        wiz_dict = {
            'product': self.product_noper.id,
            'supplier': self.supplier1.id,
            'name': self.supplier1.name,
            'stock_period_min': self.supplier1.name.stock_period_min,
            'stock_period_max': self.supplier1.name.stock_period_max,
            'ultimate_purchase_to': dateplanned,
        }
        tstwiz = self.env['purchase.purchase_wizard'].create(wiz_dict)
        purchase = tstwiz.create_rfq()
        res = tstwiz.with_context(
            active_ids=self.product_noper.ids).default_get([])
        self.assertEqual(False, res['ultimate_purchase'])
        self.assertEqual(0.0, res['stock_avl'])
        # product ultimate purchase should be false now
        # testing update_proposal
        self.assertEqual(False, self.product_noper.ultimate_purchase)
        # verify PO date and PO quantity
        self.assertEqual(dateplanned, purchase.date_planned)
        self.assertEqual(
            tstwiz._get_qty(self.product_noper, self.supplier1,
                            self.supplier1.name.stock_period_max),
            purchase.order_line[0].product_qty
        )
        dateplanned = (date.today() + timedelta(days=200)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        partner = self.supplier1.name
        wiz_primary_dict = {
            'product': self.product_noper.id,
            'supplier': self.supplier1.id,
            'name': partner.id,
            'stock_period_min': self.supplier1.name.stock_period_min,
            'stock_period_max': self.supplier1.name.stock_period_max,
            'ultimate_purchase_to': dateplanned,
            'primary_supplier_only': False,
        }
        tst_primary_wiz = self.env['purchase.purchase_supplier_wizard'].create(
            wiz_primary_dict
        )
        purchase = tst_primary_wiz.create_partner_rfq()
        # the wizard is called with an active id of res.partner
        res = tst_primary_wiz.with_context(
            active_ids=[partner.id]).default_get([])
        self.assertEqual(False, res['ultimate_purchase'])
        # testing update_proposal
        self.assertEqual(False, partner.ultimate_purchase)
