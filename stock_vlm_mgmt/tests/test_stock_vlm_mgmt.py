# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests.common import Form, TransactionCase, tagged


@tagged("-at_install", "post_install")
class StockVlmMgmt(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tray_type_id = cls.env["stock.location.vlm.tray.type"].create(
            {
                "name": "Test",
                "code": "test",
                "cols": 3,
                "rows": 3,
                "width": 25,
                "depth": 50,
                "height": 100,
            }
        )
        cls.location_dest_id = cls.env.ref("stock.stock_location_stock")
        cls.location_id = cls.env.ref("stock.stock_location_suppliers")
        cls.operation_type = cls.env.ref("stock.picking_type_in")
        cls.sequence_id = cls.env["ir.sequence"].create(
            {
                "name": "Test sequence",
                "implementation": "standard",
                "active": True,
                "prefix": "TEST/",
                "padding": 5,
                "number_increment": 1,
            }
        )
        cls.location_dest_id.write(
            {
                "is_vlm": True,
                "vlm_vendor": "test",
                "vlm_hostname": "test",
                "vlm_port": "test",
                "vlm_address": "test",
                "vlm_sequence_id": cls.sequence_id.id,
            }
        )
        cls.tray_id = cls.env["stock.location.vlm.tray"].create(
            {
                "name": "Test try",
                "tray_type_id": cls.tray_type_id.id,
                "location_id": cls.location_dest_id.id,
            }
        )
        cls.product_1 = cls.env["product.product"].create(
            {"name": "product_test_1", "detailed_type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "product_test_1", "detailed_type": "product"}
        )
        cls.picking_id = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.operation_type.id,
                "location_id": cls.location_id.id,
                "location_dest_id": cls.location_dest_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_1.id,
                            "name": cls.product_1.name,
                            "product_uom_qty": 10,
                            "location_id": cls.location_id.id,
                            "location_dest_id": cls.location_dest_id.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_2.id,
                            "name": cls.product_2.name,
                            "product_uom_qty": 5,
                            "location_id": cls.location_id.id,
                            "location_dest_id": cls.location_dest_id.id,
                        }
                    ),
                ],
            }
        )
        cls.picking_id.action_confirm()

    def test_stock_vlm_mgmt(self):
        self.picking_id.button_validate()
        self.assertTrue(self.picking_id.vlm_move_line_ids)
        self.assertTrue(self.picking_id.vlm_pending_move_line_ids)
        self.assertTrue(self.picking_id.has_vlm_operations)
        self.assertTrue(self.picking_id.has_vlm_pending_operations)
        self.assertTrue(self.picking_id.vlm_task_ids)
        self.assertEqual(len(self.picking_id.vlm_task_ids), 2)
        self.assertTrue(self.picking_id.has_pending_vlm_tasks)
        with Form(
            self.env["stock.vlm.task.action"].with_context(
                default_vlm_task_id=self.picking_id.vlm_task_ids[0].id,
                default_vlm_task_ids=self.picking_id.vlm_task_ids.ids,
            )
        ) as wizard:
            self.assertEqual(wizard.vlm_task_id, self.picking_id.vlm_task_ids[0])
            self.assertEqual(wizard.next_vlm_task_id, self.picking_id.vlm_task_ids[1])
            wizard.tray_id = self.tray_id
            wizard.quantity_done = wizard.quantity_pending
            wizard.save()
            wizard.record.action_manual_set()
            self.assertEqual(wizard.record.state, "done")
            self.assertEqual(self.picking_id.vlm_task_ids[0].state, "done")
