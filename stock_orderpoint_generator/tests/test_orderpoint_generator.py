# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.exceptions import UserError
from openerp.tests import TransactionCase


class TestOrderpointGenerator(TransactionCase):

    def setUp(self):
        super(TestOrderpointGenerator, self).setUp()

        self.wizard_model = self.env['stock.warehouse.orderpoint.generator']

        self.orderpoint_model = self.env['stock.warehouse.orderpoint']

        self.orderpoint_template_model = self.env[
            'stock.warehouse.orderpoint.template'
        ]

        self.product_model = self.env['product.product']
        self.p1 = self.product_model.create({'name': 'Unittest P1'})
        self.p2 = self.product_model.create({'name': 'Unittest P2'})

        self.assertEqual(0, self.orderpoint_model.search_count([
            ('name', '=', 'OP/000445')
        ]))

        self.template = self.orderpoint_template_model.create({
            'company_id': self.ref('base.main_company'),
            'location_id': self.ref('stock.stock_location_stock'),
            'name': 'OP/000445',
            'product_max_qty': 15.0,
            'product_min_qty': 5.0,
            'qty_multiple': 1,
            'warehouse_id': self.ref('stock.warehouse0')
        })

    def check_orderpoint(self):
        orderpoints = self.orderpoint_model.search([
            ('name', '=', 'OP/000445')
        ], order='product_id')

        self.assertEqual(2, len(orderpoints))

        self.assertEqual(self.p1, orderpoints[0].product_id)
        self.assertEqual(self.p2, orderpoints[1].product_id)

        for orderpoint in orderpoints:
            for field in ('company_id', 'location_id', 'product_max_qty',
                          'product_min_qty', 'qty_multiple', 'warehouse_id'):
                self.assertEqual(orderpoint[field], self.template[field])

    def test_product_orderpoint(self):

        wizard = self.wizard_model.with_context(
            active_ids=[self.p1.id, self.p2.id]
        ).create({
            'orderpoint_template_id': [(6, 0, [self.template.id])]
        })
        wizard.action_configure()

        self.check_orderpoint()

    def test_template_orderpoint(self):

        wizard = self.wizard_model.with_context(
            active_model='product.template',
            active_ids=[self.p1.product_tmpl_id.id, self.p2.product_tmpl_id.id]
        ).create({
            'orderpoint_template_id': [(6, 0, [self.template.id])]
        })
        wizard.action_configure()

        self.check_orderpoint()

    def test_template_variants_orderpoint(self):

        self.product_model.create({
            'product_tmpl_id': self.p1.product_tmpl_id.id,
            'name': 'Unittest P1 variant'
        })

        wizard = self.wizard_model.with_context(
            active_model='product.template',
            active_ids=[self.p1.product_tmpl_id.id]
        ).create({
            'orderpoint_template_id': [(6, 0, [self.template.id])]
        })
        with self.assertRaises(UserError):
            wizard.action_configure()
