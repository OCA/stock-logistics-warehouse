# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields

from odoo.addons.stock_vertical_lift.tests.common import VerticalLiftCase


class TestPick(VerticalLiftCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param(
            "vertical_lift_empty_tray_check", True
        )

    def _test_location_empty_common(self, operation, tray_is_empty):
        """Common part for tests checking the tray location is empty

        Returns the new inventory adjustment created."""
        self.assertEqual(operation.state, "scan_destination")
        move_line = operation.current_move_line_id
        customers_location = self.env.ref("stock.stock_location_customers")
        customers_location.barcode = "CUSTOMERS"
        operation.on_barcode_scanned(customers_location.barcode)
        self.assertEqual(move_line.location_dest_id, customers_location)
        self.assertEqual(operation.state, "save")
        operation.button_save()
        self.assertEqual(operation.state, "release")
        self.assertEqual(operation.tray_qty, 0)
        res_dict = operation.button_release()
        wizard = self.env[(res_dict.get("res_model"))].browse(res_dict.get("res_id"))
        wizard = wizard.with_context(
            active_id=operation.id, active_model=operation._name
        )
        domain = [
            ("product_id", "=", move_line.product_id.id),
            "|",
            ("location_dest_id", "=", move_line.location_id.id),
            ("location_id", "=", move_line.location_id.id),
            ("date", ">=", fields.Date.today()),
            ("is_inventory", "=", True),
        ]
        # breakpoint()
        moves_before = self.env["stock.move"].search(domain)
        # tray_location = operation.tray_location_id
        # tray_product = operation.current_move_line_id.product_id
        if tray_is_empty:
            # Case 1.1
            wizard.button_confirm_empty()
        else:
            # Case 1.2
            wizard.button_confirm_not_empty()

        domain += [("id", "not in", moves_before.ids)]
        return self.env["stock.move"].search(domain)

    def test_location_empty_is_empty(self):
        """Location is indicated as being empty, and it is"""
        operation = self._open_screen("pick")
        move = self._test_location_empty_common(operation, tray_is_empty=True)

        self.assertEqual(len(move), 1)
        self.assertEqual(move.product_qty, 0)
        # self.assertEqual(inventory.state, "done")

    def test_location_empty_is_not_empty(self):
        """Location is indicated as being empty, but it is not."""
        operation = self._open_screen("pick")
        # tray_location = operation.tray_location_id
        # tray_product = operation.current_move_line_id.product_id
        move = self._test_location_empty_common(operation, tray_is_empty=False)

        self.assertEqual(len(move), 1)
        self.assertEqual(move.product_qty, 1)
        # self.assertEqual(inventory.state, "draft")
        # self.assertEqual(inventory.product_ids, tray_product)
        # self.assertEqual(inventory.location_ids, tray_location)
