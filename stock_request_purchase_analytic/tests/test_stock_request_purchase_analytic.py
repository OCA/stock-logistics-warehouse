# Copyright 2017-2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.stock_request_purchase.tests \
    import test_stock_request_purchase
from odoo import fields


class TestStockRequestPurchaseAnalytic(
        test_stock_request_purchase.TestStockRequestPurchase):

    def setUp(self):
        super(TestStockRequestPurchaseAnalytic, self).setUp()
        self.analytic_model = self.env['account.analytic.account']
        self.analytic = self.analytic_model.create({'name': 'XX'})

    def test_create_request_01(self):
        """Single Stock request with buy rule"""
        expected_date = fields.Datetime.now()
        vals = {
            'company_id': self.main_company.id,
            'expected_date': expected_date,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product.id,
                'analytic_account_id': self.analytic.id,
                'product_uom_id': self.product.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'expected_date': expected_date,
            })]
        }

        order = self.env['stock.request.order'].sudo(
            self.stock_request_user).create(vals)
        order.action_confirm()
        order.refresh()
        po_lines = order.sudo().purchase_line_ids
        self.assertEqual(po_lines.account_analytic_id, self.analytic)
