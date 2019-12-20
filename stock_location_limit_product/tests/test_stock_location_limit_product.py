# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestStockLocationLimitProduct(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestStockLocationLimitProduct, self).setUp(*args, **kwargs)

        self.location_3 = self.env.ref('stock.stock_location_3')
        self.product_2 = self.env.ref('product.product_product_1')

    def test_write(self):

        self.location_3.write(
            {'limit_ids': [(
                0, 0, {'product_id': self.product_2.id, 'qty': 2})]})
