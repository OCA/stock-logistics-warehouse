# © 2020 FactorLibre
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestStockReserveSale(TransactionCase):

    def setUp(self):
        super(TestStockReserveSale, self).setUp()

        # Models
        self.res_partner_model = self.env['res.partner']
        self.product_model = self.env['product.product']
        self.product_category_model = self.env['product.category']
        self.sale_order_model = self.env['sale.order']
        self.sale_stock_reserve_model = self.env['sale.stock.reserve']
        self.wizard_model = self.env['stock.change.product.qty']
        self.stock_location_model = self.env['stock.location']

        # Models Data
        self.stock_valuation_account = self.env['account.account'].create({
            'name': 'Stock Valuation',
            'code': 'Stock Valuation',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id
            })

        self.category = self.product_category_model.create({
            'name': 'Physical (test)',
            'property_cost_method': 'standard',
            'property_valuation': 'real_time',
            'property_stock_valuation_account_id':
                self.stock_valuation_account.id
            })

        self.product_gelato1 = self._product_create('001GELATO', 'Gelato 1')
        self.product_gelato2 = self._product_create('002GELATO', 'Gelato 2')
        self.partner_test = self.res_partner_model.create({
                'name': 'Partner Test',
            })

        self.sale_order_gelato = self.sale_order_model.create({
            'partner_id': self.partner_test.id,
            'partner_invoice_id': self.partner_test.id,
            'partner_shipping_id': self.partner_test.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'order_line': [
                (0, 0, {
                    'name': self.product_gelato1.name,
                    'product_id': self.product_gelato1.id,
                    'product_uom_qty': 4,
                    'product_uom': self.product_gelato1.uom_id.id,
                    'price_unit': self.product_gelato1.list_price,
                    'tax_id': [(6, 0, [])]
                    }),
                (0, 0, {
                    'name': self.product_gelato2.name,
                    'product_id': self.product_gelato2.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product_gelato2.uom_id.id,
                    'price_unit': self.product_gelato2.list_price,
                    'tax_id': [(6, 0, [])]
                    }), ],
            })

    def _product_create(self, default_code, name):
        product_uom_kgm = self.env.ref('product.product_uom_kgm')
        return self.product_model.create({
            'default_code': default_code,
            'name': name,
            'type': 'product',
            'categ_id': self.category.id,
            'list_price': 100.0,
            'standard_price': 70.0,
            'uom_id': product_uom_kgm.id,
            'uom_po_id': product_uom_kgm.id,
            'valuation': 'real_time',
            'cost_method': 'average',
        })

    def test_sale_order_reservation(self):
        context = {
            'active_id': self.sale_order_gelato.id,
            'active_ids': [self.sale_order_gelato.id],
            'active_model': 'sale.order',
        }

        self.sale_stock_reserve_gelato = self.sale_stock_reserve_model.\
            with_context(context).create({})
        self.sale_stock_reserve_gelato.button_reserve()

        self.assertEqual(self.product_gelato1.virtual_available, -4)
        self.assertEqual(self.product_gelato2.virtual_available, -1)

        self.sale_order_gelato.release_all_stock_reservation()

        self.assertEqual(self.product_gelato1.virtual_available, 0)
        self.assertEqual(self.product_gelato2.virtual_available, 0)

    def test_sale_order_line_reservation(self):

        sale_order_line_gelato1 = ''
        for sale_line in self.sale_order_gelato.order_line:
            if sale_line.product_id.id == self.product_gelato1.id:
                sale_order_line_gelato1 = sale_line
                break

        context = {
            'active_id': sale_order_line_gelato1.id,
            'active_ids': [sale_order_line_gelato1.id],
            'active_model': 'sale.order.line',
        }

        self.sale_stock_reserve_gelato = self.sale_stock_reserve_model.\
            with_context(context).create({})
        self.sale_stock_reserve_gelato.button_reserve()

        self.assertEqual(self.product_gelato1.virtual_available, -4)
        self.assertEqual(self.product_gelato2.virtual_available, 0)

        self.sale_order_gelato.release_all_stock_reservation()

        self.assertEqual(self.product_gelato1.virtual_available, 0)
        self.assertEqual(self.product_gelato2.virtual_available, 0)
