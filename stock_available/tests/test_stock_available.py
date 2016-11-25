# -*- coding: utf-8 -*-
# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockLogisticsWarehouse(TransactionCase):

    def test_res_config(self):
        """Test the config file"""
        stock_setting = self.env['stock.config.settings'].create({})

        self.assertEquals(
            stock_setting.stock_available_mrp_based_on,
            'qty_available')
        stock_setting.stock_available_mrp_based_on = 'immediately_usable_qty'
        stock_setting.set_stock_available_mrp_based_on()
        self.assertEquals(
            stock_setting.stock_available_mrp_based_on,
            'immediately_usable_qty')
