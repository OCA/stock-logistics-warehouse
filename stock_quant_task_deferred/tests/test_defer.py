# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.queue_job.tests.common import trap_jobs


class TestDeferQuantTask(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
            }
        )

    def test_defer_quant_tasks_not_deferred(self):
        # Check the normal process
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "location_id": self.stock.id,
                "product_id": self.product.id,
                "inventory_quantity": 0.0,
            }
        )._apply_inventory()
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.stock.id)]
        )
        self.assertTrue(quant)
        self.env["stock.quant"].action_view_inventory()
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.stock.id)]
        )
        self.assertFalse(quant)

    def test_defer_quant_tasks(self):
        # No more quant tasks are done
        self.env.company.defer_quant_tasks = True
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "location_id": self.stock.id,
                "product_id": self.product.id,
                "inventory_quantity": 0.0,
            }
        )._apply_inventory()
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.stock.id)]
        )
        self.assertTrue(quant)
        self.env["stock.quant"].action_view_inventory()
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.stock.id)]
        )
        self.assertTrue(quant)

        # Call _quant_tasks() with run
        self.env["stock.quant"].with_context(run_defer_quant_tasks=True)._quant_tasks()
        self.assertFalse(quant.exists())

    def test_defer_quant_tasks_cron(self):
        # Quant tasks are done through a cron job
        # that trigger a queue job.
        self.env.company.defer_quant_tasks = True
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "location_id": self.stock.id,
                "product_id": self.product.id,
                "inventory_quantity": 0.0,
            }
        )._apply_inventory()
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.stock.id)]
        )
        self.assertTrue(quant)
        self.env["stock.quant"].action_view_inventory()
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.stock.id)]
        )
        self.assertTrue(quant)

        # Call _quant_tasks() with run
        with trap_jobs() as trap:
            self.env["stock.quant"]._run_quant_tasks_deferred()
            trap.assert_enqueued_job(self.env["stock.quant"]._quant_tasks_deferred)
            trap.perform_enqueued_jobs()
        self.assertFalse(quant.exists())
