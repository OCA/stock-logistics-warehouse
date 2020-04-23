# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase
from .common import TestExcludeLocationMixin, ExcludeLocationModelFake


class TestExcludeLocation(SavepointCase, TestExcludeLocationMixin):

    @classmethod
    def setUpClass(cls):
        super(TestExcludeLocation, cls).setUpClass()
        ExcludeLocationModelFake._test_setup_model(cls.env)
        cls.fake = cls.env["exclude.location.fake"].create({})
        cls.location_shop = cls.env.ref("stock.stock_location_shop0")
        vals = {
            "location_id": cls.location_shop.id,
            "name": "Sub Location 1"
        }
        cls.sub_location_1 = cls.env["stock.location"].create(vals)
        cls.sub_location_1._parent_store_compute()
        cls.product = cls.env.ref("product.product_product_4")

    @classmethod
    def tearDownClass(cls):
        ExcludeLocationModelFake._test_teardown_model(cls.env)
        super(TestExcludeLocation, cls).tearDownClass()

    def _add_stock_to_product(self, product, location, qty):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        """
        wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "new_quantity": qty,
                "location_id": location.id,
            }
        )
        wizard.change_product_qty()

    def test_exclude_location(self):
        # Add different levels of stock for product as :
        # Shop 0: 50.0
        # Sub Level (Shop 0 / Sub Location 1): 25.0
        # Query product stock availability normally and with excluded
        # location as Sub Location 1
        self._add_stock_to_product(self.product, self.location_shop, 50.0)
        self._add_stock_to_product(self.product, self.sub_location_1, 25.0)
        self.fake.stock_excluded_location_ids = self.sub_location_1
        qty = self.product.with_context(
            excluded_location_ids=self.fake.stock_excluded_location_ids).\
            qty_available
        self.assertEquals(
            50.0,
            qty
        )
        qty = self.product.qty_available
        self.assertEquals(
            75.0,
            qty
        )
