# -*- coding: utf-8 -*-
# Copyright 2016-18 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestGeneratePutaway(TransactionCase):
    """Test that the putaway locations are updated when the method is used"""

    def test_generate(self):
        """Test default methods"""
        self.product_10 = self.env.ref('product.product_product_10')
        self.product_25 = self.env.ref('product.product_product_25')
        inventory = self.env.ref('stock.stock_inventory_0')
        self.env['stock.inventory.line'].create({
            'product_id': self.product_25.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
            'inventory_id': inventory.id,
            'product_qty': 1.0,
            'location_id': self.ref('stock.stock_location_components'),
        })
        inventory.generate_putaway_strategy()
        self.assertEquals(
            len(self.product_25.product_putaway_ids), 1,
            'pas le bon nombre de putaway strategy créées')
        self.assertEquals(
            self.product_10.product_putaway_ids.fixed_location_id.id,
            self.ref('stock.stock_location_components'))
        self.assertEquals(
            self.product_10.product_putaway_ids.putaway_id.id,
            self.ref('stock_putaway_product.product_putaway_per_product_wh'))
        self.assertEquals(
            self.product_25.product_putaway_ids.fixed_location_id.id,
            self.ref('stock.stock_location_14'))
