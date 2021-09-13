# Copyright 2016 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


class TestAutomaticWorkflowStockReservation(TestAutomaticWorkflowMixin, TestCommon):
    def test_workflow_stock_reservation(self):
        workflow = self.create_full_automatic(
            override={
                "name": "Workflow Automatic Reservation",
                "validate_order": False,
                "create_invoice": False,
                "stock_reservation": True,
                "stock_reservation_validity": 5,
            }
        )
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.is_stock_reservable, True)
        self.assertEqual(sale.has_stock_reservation, False)
        self.run_job()
        self.assertEqual(sale.has_stock_reservation, True)

    def test_workflow_automatic_no_reservation(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.is_stock_reservable, True)
        self.assertEqual(sale.has_stock_reservation, False)
        self.run_job()
        self.assertEqual(sale.state, "sale")
        self.assertEqual(sale.has_stock_reservation, False)
