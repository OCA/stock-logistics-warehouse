# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, timedelta

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tests.common import TransactionCase


class TestStockReorderForecast(TransactionCase):

    def setUp(self):
        super(TestStockReorderForecast, self).setUp()
        self.model_data_obj = self.env['ir.model.data']
        self.sale_order_obj = self.env['sale.order']
        self.product_obj = self.env['product.product']
        self.stock_pack_obj = self.env['stock.pack.operation']
        self.picking_obj = self.env['stock.picking']
        self.move_obj = self.env['stock.move']
        self.partner_delta_id = self.model_data_obj.xmlid_to_res_id(
            'base.res_partner_4'
        )
        self.partner_agrolite_id = self.model_data_obj.xmlid_to_res_id(
            'base.res_partner_2'
        )
        self.picking_type_in = self.model_data_obj.xmlid_to_res_id(
            'stock.picking_type_in'
        )
        self.picking_type_out = self.model_data_obj.xmlid_to_res_id(
            'stock.picking_type_out'
        )
        self.supplier_location = self.model_data_obj.xmlid_to_res_id(
            'stock.stock_location_suppliers'
        )
        self.stock_location = self.model_data_obj.xmlid_to_res_id(
            'stock.stock_location_stock'
        )

        self.product_noper = self.env.ref(
            'stock_reorder_forecast.product_noper')
        self.product_period90 = self.env.ref(
            'stock_reorder_forecast.product_period90')
        self.product_period180 = self.env.ref(
            'stock_reorder_forecast.product_period180')
        self.supplier1 = self.env.ref(
            'stock_reorder_forecast.product_supplierinfo_1'
        )

    def test_calc_purchase_date(self):
        self.product_obj.calc_purchase_date()
        # No sale orders and product with no period
        self.assertEqual(0.0, self.product_noper.turnover_average)
        self.assertEqual(False, self.product_noper.ultimate_purchase)
        # No sale orders and product with period 90
        self.assertEqual(0.0, self.product_period90.turnover_average)
        self.assertEqual(False, self.product_period90.ultimate_purchase)
        # test  _get_turnover_period
        # turnover period will be 1 because this p-roduct has been just created
        # we predate it after

        self.assertEqual(1, self.product_period90._get_turnover_period())
        self.assertEqual(
            1,
            self.product_noper._get_turnover_period()
        )
        # Create sale order for product noperiod
        so1 = self.sale_order_obj.create({
            'partner_id': self.partner_agrolite_id,
            'partner_invoice_id': self.partner_agrolite_id,
            'partner_shipping_id': self.partner_agrolite_id,
            'order_line': [(0, 0, {'name': self.product_noper.name,
                                   'product_id': self.product_noper.id,
                                   'product_uom_qty': 184,
                                   'product_uom': self.product_noper.uom_id.id,
                                   'price_unit': 75})],
            'pricelist_id': self.env.ref('product.list0').id, })
        self.product_obj.calc_purchase_date()
        # should still be a still 0

        self.assertEqual(0.0, self.product_noper.turnover_average)
        self.assertEqual(False, self.product_noper.ultimate_purchase)
        self.assertEqual(0.00, self.product_period90.turnover_average)
        self.assertEqual(False, self.product_period90.ultimate_purchase)
        so1.action_button_confirm()
        self.product_obj.calc_purchase_date()
        self.assertEqual(184.0, self.product_noper.turnover_average)
        self.assertEqual(0.0, self.product_period90.turnover_average)
        # create and confirm 2 sale orders for the 90 day period
        so2 = self.sale_order_obj.create({
            'partner_id': self.partner_agrolite_id,
            'partner_invoice_id': self.partner_agrolite_id,
            'partner_shipping_id': self.partner_agrolite_id,
            'order_line': [(0, 0, {'name': self.product_period90.name,
                                   'product_id': self.product_period90.id,
                                   'product_uom_qty': 20,
                                   'product_uom':
                                       self.product_period90.uom_id.id,
                                   'price_unit': 33})],
            'pricelist_id': self.env.ref('product.list0').id, })
        so3 = self.sale_order_obj.create({
            'partner_id': self.partner_agrolite_id,
            'partner_invoice_id': self.partner_agrolite_id,
            'partner_shipping_id': self.partner_agrolite_id,
            'order_line': [(0, 0, {'name': self.product_period90.name,
                                   'product_id': self.product_period90.id,
                                   'product_uom_qty': 20,
                                   'product_uom':
                                       self.product_period90.uom_id.id,
                                   'price_unit': 33})],
            'pricelist_id': self.env.ref('product.list0').id, })
        # confirm orders
        so2.action_button_confirm()
        so3.action_button_confirm()
        self.product_obj.calc_purchase_date()
        # verify rate
        self.assertEqual(40.0, self.product_period90.turnover_average)
        # make a sale order older than 90 days and verify it does not influence
        # the resulting turnover_average

        # extra check these products are newly created so the period will not
        # be the days specified in their turnover period
        # the turnover average is calculated on ONE DAY because the product age
        # ( time from creation date) is 1 day  and  therefore less than the
        # default product period.

        # pre-date magic field create date for product_period90 (2 years)
        sql = "update product_product set create_date=%s where id = %s"
        self.env.cr.execute(
            sql, (
                (date.today() - timedelta(days=730)).strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT),
                self.product_period90.id
            )
        )
        self.product_obj.calc_purchase_date()
        # sold 40 elements in 90 days
        self.assertEqual(40, self.product_period90.turnover_average)
        so_old = self.sale_order_obj.create({
            'partner_id': self.partner_agrolite_id,
            'partner_invoice_id': self.partner_agrolite_id,
            'partner_shipping_id': self.partner_agrolite_id,
            'order_line': [(0, 0, {'name': self.product_period90.name,
                                   'product_id': self.product_period90.id,
                                   'product_uom_qty': 20,
                                   'product_uom':
                                       self.product_period90.uom_id.id,
                                   'price_unit': 33})],
            'pricelist_id': self.env.ref('product.list0').id, })
        # pre-date the magic field create_date for sale order
        # fix, the calc function looks at date_order, not at created date
        so_old.action_button_confirm()
        sql = "update sale_order set date_order=%s where id = %s"
        self.env.cr.execute(
            sql, (
                (date.today() - timedelta(days=120)).strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT),
                so_old.id
            )
        )
        self.product_obj.calc_purchase_date()
        # verify turnover average is still the same, because latest SO is
        # before the current turnover period for this product (90)
        # sold 40 elements in the past 90 days , 60 overall
        self.assertEqual(40, self.product_period90.turnover_average)
        # verify order of period fetching
        # product_noper with supplier without turnover_period and category
        # without turnover_period and verify it gets turnover_period default
        # verify that parnter associated to  supplier has no turnover_period
        self.assertEqual(False, self.supplier1.name.turnover_period)
        # turnover period is allways 1 for a new product
        self.assertEqual(1, self.product_noper._get_turnover_period())
        # sold 184 pieces , turnover period == product age == 1
        self.assertEqual(184, self.product_noper.turnover_average)
        # pre-date magic field create date for product_period90 (2 years)
        sql = "update product_product set create_date=%s where id = %s"
        self.env.cr.execute(
            sql, (
                (date.today() - timedelta(days=730)).strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT),
                self.product_noper.id
            )
        )
        self.product_noper.write({'turnover_period': 10})
        self.product_obj.calc_purchase_date()
        # test  _get_turnover_period this time it will remain 10 (old product)
        self.assertEqual(10, self.product_noper._get_turnover_period())
        # sold 184 pieces , period 10 days
        self.product_obj.calc_purchase_date()
        self.assertEqual(18.4, self.product_noper.turnover_average)

        # assign turnover_period to supplier and verify it gets that
        self.product_noper.write({'turnover_period': 5})
        self.product_obj.calc_purchase_date()
        # test  _get_turnover_period
        self.assertEqual(5, self.product_noper._get_turnover_period())
        self.product_obj.calc_purchase_date()
        self.assertEqual(36.8, self.product_noper.turnover_average)
        # assign turnover period to product itself and veify it supercedes all
        self.product_noper.write({'turnover_period': 7})
        # test  _get_turnover_period
        self.assertEqual(7, self.product_noper._get_turnover_period())
        self.product_obj.calc_purchase_date()
        self.assertEqual(
            26.29, self.product_noper.turnover_average)

        # increase stock and  verify ultimate purchase
        # ============ STOCK TEST ==========
        # create an incoming shipment for 500  pieces
        # of product_period180,  period190 still has no RFQ so ultimate
        # purchase will not be false
        picking_in = self.picking_obj.create({
            'partner_id': self.partner_delta_id,
            'picking_type_id': self.picking_type_in,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location})
        self.move_obj.create({
            'name': self.product_noper.name,
            'product_id': self.product_period180.id,
            'product_uom_qty': 500,
            'product_uom': self.product_period180.uom_id.id,
            'picking_id': picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location})
        picking_in.action_confirm()
        picking_in.do_prepare_partial()
        self.stock_pack_obj.search(
            [('product_id', '=', self.product_period180.id),
             ('picking_id', '=', picking_in.id)]).write({'product_qty': 500})
        # Transfer Incoming Shipment.
        picking_in.do_transfer()
        self.assertEqual(500, self.product_period180.qty_available)
        # MUST DESTROY ALL PO'S GENERATED SO WE CAN GET THE RIGHT ULTIMATE
        # DATE(NOT FALSE)
        self.env.cr.execute("UPDATE PURCHASE_ORDER SET STATE='cancel'")
        so4 = self.sale_order_obj.create({
            'partner_id': self.partner_agrolite_id,
            'partner_invoice_id': self.partner_agrolite_id,
            'partner_shipping_id': self.partner_agrolite_id,
            'order_line': [(0, 0, {'name': self.product_period180.name,
                                   'product_id': self.product_period180.id,
                                   'product_uom_qty': 20,
                                   'product_uom':
                                       self.product_period180.uom_id.id,
                                   'price_unit': 33})],
            'pricelist_id': self.env.ref('product.list0').id, })
        # pre-date the magic field create_date for sale order
        sql = "update sale_order set create_date=%s where id = %s"
        so4.action_button_confirm()
        # clean up draft purchase order to test ultimate purchase correctly
        self.env.cr.execute("UPDATE PURCHASE_ORDER SET STATE='cancel'")
        self.product_obj.calc_purchase_date()
#         self.assertEqual(
#             (date.today()).strftime(
#                 DEFAULT_SERVER_DATE_FORMAT
#             ),
#             self.product_period180.ultimate_purchase
#         )

    def test_supplier_calc(self):
        # verify supplier product_ids
        # verify supplier primary product_ids
        # create a new partner and a new supplier info,
        # new_supplier COMES WITH A PRIMARY PRODUCT PRIMARY_PERIOD180

        new_supplier = self.env.ref(
            'stock_reorder_forecast.product_supplierinfo_new'
        )
        new_supplier.name._compute_product_supplierinfo()
        new_supplier.name._compute_product_supplierinfo_primary()
        # verify that the resuser associated to supplier1 has the correct prds
        # add another supplier info (with product) and verify
        # compute_product_supplierinfo
        # WE ALREADY HAVE supplier1 as primary supplier for
        # product_noper
        self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.product_period90.product_tmpl_id.id,
            'name': new_supplier.name.id,
            'delay': 1,
            'min_qty': 1,
            'sequence': 2,
        })

        # set another suppliernfo as primary for product_period90
        # it's primary because it has the highest sequence for that product

        self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.product_period180.product_tmpl_id.id,
            'name': new_supplier.name.id,
            'delay': 1,
            'min_qty': 1,
            'sequence': 2,
        })

        # supplier1 is the primary
        self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.product_period180.product_tmpl_id.id,
            'name': self.supplier1.name.id,
            'delay': 1,
            'min_qty': 1,
            'sequence': 1,
        })
        new_supplier.name._compute_product_supplierinfo()
        new_supplier.name._compute_product_supplierinfo_primary()

        # Verify that the primary products for supplier new supplier
        # is still unique
        self.assertEqual(
            self.product_period180.product_tmpl_id.id in
            new_supplier.name.primary_product_ids.ids, True
        )
        # give new_supplier. name another primary product , product_noper
        self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.product_noper.product_tmpl_id.id,
            'name': new_supplier.name.id,
            'delay': 1,
            'min_qty': 1,
            'sequence': 1,
        })
