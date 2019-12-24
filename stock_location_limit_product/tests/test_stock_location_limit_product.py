# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockLocationLimitProduct(TransactionCase):

    def setUp(self):
        super(TestStockLocationLimitProduct, self).setUp()
        self.obj_product = self.env['product.product']
        self.obj_location = self.env['stock.location']
        self.limit_obj = self.env['stock.location.limit']
        self.uom = self.env.ref("uom.product_uom_unit")
        self.product = self.obj_product.create({
            'name': 'Test Product',
            'type': 'product',
            'default_code': 'PROD',
            'uom_id': self.uom.id,
        })
        self.product2 = self.obj_product.create({
            'name': 'Test Product2',
            'type': 'product',
            'default_code': 'PROD',
            'uom_id': self.uom.id,
        })

        self.location = self.obj_location.create({
            'name': 'Test Location',
            'usage': 'internal',
        })

    def test_onchange_uom_id(self):
        limit = self.limit_obj
        with self.assertRaises(ValidationError):
            # constrain is called when create a record.
            limit = self.limit_obj.create({
                'location_id': self.location.id,
                'product_id': self.product.id,
                'qty': 100,
            })
        if not limit:
            limit = self.limit_obj.create({
                'location_id': self.location.id,
                'product_id': self.product2.id,
                'qty': 100,
                'uom_id': self.uom.id,
            })
            limit.onchange_uom_id()
            limit.check_uom_id()
            limit_count = len(self.limit_obj.search([]))
            self.assertEqual(limit_count, 2)
            self.assertEqual(limit.uom_id.id, self.uom.id)
