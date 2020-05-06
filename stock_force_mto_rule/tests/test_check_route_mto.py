# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCheckRouteMTO(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestCheckRouteMTO, self).setUp(*args, **kwargs)
        product_obj = self.env['product.product']
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']

        mto_route = self.env.ref('stock.route_warehouse0_mto')
        partner = self.env.ref('base.res_partner_1')

        # Create Products:
        product_1 = product_obj.create({
            'name': 'Test Product 1',
            'type': 'product',
            'default_code': 'PROD1',
        })
        product_2 = product_obj.create({
            'name': 'Test Product 2',
            'type': 'product',
            'default_code': 'PROD2',
            'route_ids': [(6, 0, [mto_route.id])],
        })

        # Create a sale order with 2 lines:
        order = sale_obj.create({
            'partner_id': partner.id,
        })
        order.onchange_partner_id()
        line_1_vals = self.get_sale_order_line_vals(product_1, order.id)
        self.line_1 = sale_line_obj.create(line_1_vals)
        line_2_vals = self.get_sale_order_line_vals(product_2, order.id)
        self.line_2 = sale_line_obj.create(line_2_vals)

    def get_sale_order_line_vals(self, product, order_id):
        sale_line_vals = {
            'product_id': product.id,
            'name': product.name,
            'product_uom_qty': 1.0,
            'order_id': order_id,
        }
        return sale_line_vals

    def test_write_route_mto(self):
        # Check initial route_mto value:
        self.assertEqual(self.line_1.route_mto, False)
        # because product_2 has stock.route_warehouse0_mto in route_ids:
        self.assertEqual(self.line_2.route_mto, True)

        # Edit the boolean route_mto:
        self.line_1.write({'route_mto': True})
        self.assertEqual(self.line_1.route_mto, True)

        self.line_2.write({'route_mto': False})
        # because product_2 has stock.route_warehouse0_mto in route_ids:
        self.assertEqual(self.line_2.route_mto, True)
