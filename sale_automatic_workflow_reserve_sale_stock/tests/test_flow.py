# -*- coding: utf-8 -*-
# © 2016 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.addons.sale_automatic_workflow.tests.test_flow import \
    TestAutomaticWorkflow


class TestAutomaticWorkflowStockReservation(TestAutomaticWorkflow):

    def test_workflow_stock_reservation(self):
        workflow = self._create_full_automatic({
            'name': 'Workflow Automatic Reservation',
            'validate_order': False,
            'invoice_quantity': 'procurement',
            'order_policy': 'picking',
            'stock_reservation': True,
            'stock_reservation_validity': 5
        })
        sale = self._create_sale_order(workflow)
        sale.onchange_workflow_process_id()
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(sale.is_stock_reservable, True)
        self.assertEqual(sale.has_stock_reservation, False)
        self.progress()
        self.assertEqual(sale.has_stock_reservation, True)

    def test_workflow_automatic_no_reservation(self):
        workflow = self._create_full_automatic()
        sale = self._create_sale_order(workflow)
        sale.onchange_workflow_process_id()
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(sale.is_stock_reservable, True)
        self.assertEqual(sale.has_stock_reservation, False)
        self.progress()
        self.assertEqual(sale.state, 'progress')
        self.assertEqual(sale.has_stock_reservation, False)
