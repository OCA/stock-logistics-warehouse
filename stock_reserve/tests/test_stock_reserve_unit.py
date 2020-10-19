
# -*- encoding: utf-8 -*-
# Copyright 2020 InfinityloopSistemas - JulianRam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime
from odoo.tests.common import SavepointCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class StockReserve(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.uom_kgm = cls.env.ref('uom.product_uom_kgm')
        cls.uom_gram = cls.env.ref('uom.product_uom_gram')

        # I create a product to test the stock reservation

        cls.product_sorbet = cls.env['product.product'].create({
            'default_code': '001SORBET',
            'name': 'Sorbet',
            'type': 'product',
            'categ_id': cls.env.ref('product.product_category_1').id,
            'list_price': 100.0,
            'standard_price': 70.0,
            'uom_id': cls.uom_kgm.id,
            'uom_po_id': cls.uom_kgm.id
        })

        # I update the current stock of the Sorbet with 10 kgm
        cls.env['stock.change.product.qty'].create({
            'product_id': cls.product_sorbet.id,
            'new_quantity': 10.0,
            'location_id': cls.stock_location.id
        }).change_product_qty()

        cls.wh = cls.env["stock.warehouse"].search([])

        #  I create a stock orderpoint for the product

        cls.sorbet_orderpoint = cls.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': cls.wh[0].id,
            'location_id': cls.stock_location.id,
            'product_id': cls.product_sorbet.id,
            'product_uom': cls.uom_kgm.id,
            'product_min_qty': 4.0,
            'product_max_qty': 15.0,
        })

    def test_stock_reserve(self):
        # I create a stock reservation for 6 kgm
        reserv_sorbet1 = self.env['stock.reservation'].create({
            'product_id': self.product_sorbet.id,
            'product_uom_qty': 6.0,
            'product_uom': self.uom_kgm.id,
            'name': 'reserve 6 kg of sorbet for test'
        })

        #  I create a stock reservation for 500g
        reserv_sorbet2 = self.env['stock.reservation'].create({
            'product_id': self.product_sorbet.id,
            'product_uom_qty': 500,
            'product_uom': self.uom_gram.id,
            'name': 'reserve 500g of sorbet for test'
        })

        # I check Virtual stock of Sorbet after update stock.

        self.assertEqual(
            self.product_sorbet.virtual_available,
            10,
            "Stock is not updated.")

        # I create a stock reservation for 6 kgm and reserve

        reserv_sorbet1.reserve()

        #  I create a stock reservation for 500g

        reserv_sorbet2.reserve()

        # I check the reserved amount of the product and the template

        self.assertEqual(self.product_sorbet.reservation_count, 6.5)
        self.assertEqual(
            self.product_sorbet.product_tmpl_id.reservation_count, 6.5)

        # Then the reservation should be assigned and have reserved a quant

        self.assertEqual(reserv_sorbet2.state, 'assigned')
        self.assertEqual(reserv_sorbet2.reserved_availability, 500)

        # I check Virtual stock of Sorbet after update reservation

        self.assertEqual(self.product_sorbet.virtual_available, 3.5)

        # I run the scheduler

        self.env['procurement.group'].run_scheduler()

        # I release the reservation
        reserv_sorbet1.release()
        # I check Virtual stock of Sorbet after update reservation
        self.assertEqual(
            self.product_sorbet.virtual_available,
            9.5,
            "Stock is not updated.")

        # I set the validity of the second reservation to yesterday
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime(DEFAULT_SERVER_DATE_FORMAT)
        reserv_sorbet2.write({'date_validity': yesterday})
        # I call the function releasing expired reservations
        self.env['stock.reservation'].release_validity_exceeded()
        # I check Virtual stock of Sorbet after update reservation
        self.product_sorbet.refresh()
        self.assertEqual(
            self.product_sorbet.virtual_available,
            10.0,
            "Stock is not updated.")

        # I create a stock reservation for 3 kgm

        reserv_sorbet3 = self.env['stock.reservation'].create({
            'product_id': self.product_sorbet.id,
            'product_uom_qty': 3.0,
            'product_uom': self.uom_kgm.id,
            'name': 'reserve 3 kg of sorbet for test (release on unlink)'
        })

        reserv_sorbet3.reserve()
        move = reserv_sorbet3.move_id
        action_dict = reserv_sorbet3.open_move()
        self.assertEqual(
            action_dict['res_model'],
            'stock.move',
            "action model is not 'stock.move'")
        self.assertEqual(
            action_dict['res_id'],
            move.id,
            "action res_id is not correct")
        self.assertEqual(
            action_dict['id'],
            self.env.ref('stock.stock_move_action').id,
            "action not correct")
        self.assertEqual(
            action_dict['views'][0][0],
            self.env.ref('stock.view_move_form').id,
            "action view not correct")

        # I press button 'action_view_reservations' on product variant and test
        # result
        action_dict = self.product_sorbet.action_view_reservations()
        self.assertEqual(
            action_dict['res_model'],
            'stock.reservation',
            "action model is not 'stock.move'")
        self.assertTrue(action_dict['domain'], "wrong domain")
        self.assertEqual(
            action_dict['domain'][0],
            ('product_id',
             '=',
             self.product_sorbet.id),
            "action domain is not correct")
        self.assertEqual(
            action_dict['id'],
            self.env.ref('stock_reserve.action_stock_reservation_tree').id,
            "action not correct")
        self.assertEqual(
            action_dict['context']['search_default_draft'],
            1,
            "wrong context")
        self.assertEqual(
            action_dict['context']['search_default_reserved'],
            1,
            "wrong context")

        # I press button 'action_view_reservations' on product template and
        # test result
        product = self.product_sorbet
        product_tmpl = product.product_tmpl_id
        product_ids = product_tmpl.mapped('product_variant_ids.id')
        action_dict = product_tmpl.action_view_reservations()

        self.assertEqual(
            action_dict['res_model'],
            'stock.reservation',
            "action model is not 'stock.move'")
        self.assertTrue(len(action_dict['domain']), "wrong domain")
        self.assertEqual(
            action_dict['domain'][0][:2],
            ('product_id', 'in'), "action domain is not correct")
        self.assertEqual(set(action_dict['domain'][0][-1]), set(product_ids))
        self.assertEqual(
            action_dict['id'],
            self.env.ref('stock_reserve.action_stock_reservation_tree').id,
            "action not correct")
        self.assertEqual(
            action_dict['context']['search_default_draft'],
            1,
            "wrong context")
        self.assertEqual(
            action_dict['context']['search_default_reserved'],
            1,
            "wrong context")

        # I unlink the reservation
        reserv = reserv_sorbet3
        move = reserv.move_id
        reserv.unlink()
        self.assertEqual(move.state, 'cancel', "Stock move not canceled.")
