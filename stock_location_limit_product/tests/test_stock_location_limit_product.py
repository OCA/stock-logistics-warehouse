# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase
import datetime


class TestStockLocationLimitProduct(TransactionCase):

    def setUp(self):
        super(TestStockLocationLimitProduct, self).setUp()

        self.limit_obj = self.env['stock.location.limit']
        self.product = self.obj_product.create({
            'name': 'Test Product',
            'type': 'product',
            'default_code': 'PROD',
            'uom_id': self.env.ref("uom.product_uom_unit").id,
        })
        self.location = self.obj_location.create({
            'name': 'Test Location',
            'usage': 'internal',
        })

    def test_onchange_uom_id(self):
        limit = self.limit_obj.create({
            'location_id': self.location.id,
            'product_id': self.product.id,
            'quantity': 100,
        })

        limit.onchange_uom_id()
        limit.check_uom_id()
        limit_count = len(self.limit_obj.search([]))
        self.assertEqual(limit_count, 1)
        self.assertEqual(limit.uom_id.id,
                         self.env.ref("uom.product_uom_unit").id)
