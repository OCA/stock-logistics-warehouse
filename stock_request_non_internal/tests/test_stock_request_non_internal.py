# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.addons.stock_request.tests import test_stock_request
from odoo.exceptions import ValidationError


class TestStockRequestNonInternal(test_stock_request.TestStockRequest):
    def setUp(self):
        super(TestStockRequestNonInternal, self).setUp()
        self.out_location = self.env['stock.location'].create(
            {'name': 'out_loc',
             'location_id': self.warehouse.lot_stock_id.id,
             'usage': 'internal',
             'company_id': False}
        )

    def test_stock_non_internal(self):
        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 4.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.out_location.id,
        }
        self.product.route_ids = [(6, 0, self.route.ids)]
        self.env['stock.request'].sudo(
            self.stock_request_user).create(vals)

        vals = {
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_uom_qty': 4.0,
            'company_id': self.company_2.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.out_location.id,
        }
        with self.assertRaises(ValidationError):
            self.env['stock.request'].sudo(
                self.stock_request_user).create(vals)
