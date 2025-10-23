# Copyright 2019 Camptocamp SA
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from .common import VerticalLiftCase


class TestInventory(VerticalLiftCase):
    def test_switch_inventory(self):
        self.shuttle.switch_inventory()
        self.assertEqual(self.shuttle.mode, "inventory")
        self.assertEqual(
            self.shuttle._operation_for_mode().quant_id,
            self.env["stock.quant"].browse(),
        )

    def test_inventory_action_open_screen(self):
        self.shuttle.switch_inventory()
        action = self.shuttle.action_open_screen()
        operation = self.shuttle._operation_for_mode()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.operation.inventory")
        self.assertEqual(action["res_id"], operation.id)

    def test_inventory_actions(self):
        self.shuttle.switch_inventory()
        action = self.shuttle.action_menu()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.shuttle")
        self.assertEqual(action["res_id"], self.shuttle.id)

        action = self.shuttle.action_back_to_settings()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.shuttle")
        self.assertEqual(action["res_id"], 0)

        action = self.shuttle.action_manual_barcode()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.shuttle.manual.barcode")
        self.assertEqual(action["name"], "Barcode")

        operation = self._open_screen("put")
        self.assertEqual(operation._name, "vertical.lift.operation.put")
        self.assertEqual(operation.state, "scan_source")
        VerticalLiftShuttleManualBarcode = self.env[action["res_model"]]

        ClassWithContextOnlyModel = VerticalLiftShuttleManualBarcode.with_context(
            active_model=operation._name,
        )
        vls_manual_form = Form(ClassWithContextOnlyModel)
        rec_id = vls_manual_form._values.get("id")
        vls_manual = ClassWithContextOnlyModel.browse(rec_id)
        vls_manual.button_save()

        ClassWithContext = VerticalLiftShuttleManualBarcode.with_context(
            active_ids=operation.ids,
            active_id=operation.ids[0],
            active_model=operation._name,
        )
        vls_manual_form = Form(ClassWithContext)
        vls_manual_form.barcode = self.product_socks.barcode
        vls_manual_form.save()
        rec_id = vls_manual_form._values.get("id")
        vls_manual = ClassWithContext.browse(rec_id)
        vls_manual.button_save()

    def test_inventory_count_ops(self):
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        self._update_qty_in_location(self.location_1a_x2y1, self.product_recovery, 10)
        self._create_stock_quants(
            [
                (self.location_1a_x1y1, self.product_socks),
                (self.location_1a_x2y1, self.product_recovery),
            ]
        )
        self._update_qty_in_location(self.location_2a_x1y1, self.product_socks, 10)
        self._create_stock_quants([(self.location_2a_x1y1, self.product_socks)])

        operation = self._open_screen("inventory")
        self.assertEqual(operation.number_of_ops, 2)
        self.assertEqual(operation.number_of_ops_all, 3)

    def test_process_current_inventory(self):
        stock_quant = self._create_stock_quants(
            [(self.location_1a_x1y1, self.product_socks)]
        )[0]
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        operation = self._open_screen("inventory")
        self.assertEqual(operation.state, "quantity")
        self.assertEqual(operation.quant_id, stock_quant)
        # test the happy path, quantity is correct
        operation.quantity_input = 10.0
        result = operation.button_save()
        # state is reset
        # noop because we have no further lines
        self.assertEqual(operation.state, "noop")
        self.assertFalse(operation.quant_id)
        self.assertTrue(stock_quant.vertical_lift_done)
        expected_result = {
            "effect": {
                "fadeout": "slow",
                "message": self.env._("Congrats, you cleared the queue!"),
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }
        self.assertEqual(result, expected_result)

    def test_wrong_quantity(self):
        quant = self._create_stock_quants(
            [(self.location_1a_x1y1, self.product_socks)]
        )[0]
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        operation = self._open_screen("inventory")
        stock_quant = operation.quant_id
        self.assertEqual(stock_quant, quant)

        operation.quantity_input = 12.0
        operation.button_save()
        self.assertEqual(operation.last_quantity_input, 12.0)
        self.assertEqual(operation.quantity_input, 0.0)
        self.assertEqual(operation.state, "confirm_wrong_quantity")
        self.assertEqual(operation.quant_id, stock_quant)

        # entering the same quantity a second time validates
        operation.quantity_input = 12.0
        operation.button_save()
        self.assertFalse(operation.quant_id)
        self.assertTrue(quant.vertical_lift_done)
        self.assertEqual(quant.quantity, 12.0)
        self.assertFalse(operation.quant_id)

    def test_confirm_wrong_quantity(self):
        stock_quant = self._create_stock_quants(
            [(self.location_1a_x1y1, self.product_socks)]
        )[0]
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        operation = self._open_screen("inventory")
        current_quant = operation.quant_id
        self.assertEqual(current_quant, stock_quant)

        operation.quantity_input = 12.0
        operation.button_save()
        self.assertEqual(operation.last_quantity_input, 12.0)
        self.assertEqual(operation.quantity_input, 0.0)
        self.assertEqual(operation.state, "confirm_wrong_quantity")
        self.assertEqual(operation.quant_id, current_quant)
        operation.button_save()
        self.assertEqual(operation.state, "quantity")

    def test_inventory_next_line(self):
        stock_quants = self._create_stock_quants(
            [
                (self.location_1a_x1y1, self.product_socks),
                (self.location_1a_x2y1, self.product_recovery),
            ]
        )
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        self._update_qty_in_location(self.location_1a_x2y1, self.product_recovery, 10)
        operation = self._open_screen("inventory")
        operation.quantity_input = 10.0
        result = operation.button_save()
        # no rainbow because still exist operation in queue
        self.assertFalse(result)
        #
        # go to next quant
        remaining_quant = stock_quants[1]
        self.assertEqual(operation.state, "quantity")
        self.assertEqual(operation.quant_id, remaining_quant)
        self.assertEqual(operation.last_quantity_input, 0.0)
        self.assertEqual(operation.quantity_input, 0.0)

    def test_inventory_locations(self):
        self.shuttle.switch_inventory()
        opr_inventory = self.shuttle._operation_for_mode()
        opr_inventory._compute_tray_data()
        opr_inventory._compute_product_packagings()
        self.assertEqual(opr_inventory.product_packagings, "")
        opr_inventory._compute_tray_qty()
        self.assertEqual(opr_inventory.tray_qty, 0.0)

        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        self._create_stock_quants([(self.location_1a_x1y1, self.product_socks)])
        self._open_screen("inventory")
        opr_inventory._compute_product_packagings()
        opr_inventory._compute_tray_qty()
        self.assertEqual(opr_inventory.tray_qty, 10)
