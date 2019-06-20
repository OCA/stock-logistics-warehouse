# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions

from .common import KardexCase


class TestKardexTrayType(KardexCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_out = cls.env.ref(
            'stock_kardex.stock_picking_out_demo_kardex_1'
        )
        # we have a move line to pick created by demo picking
        # stock_picking_out_demo_kardex_1
        cls.out_move_line = cls.picking_out.move_line_ids

    def test_switch_pick(self):
        self.kardex.switch_pick()
        self.assertEqual(self.kardex.mode, 'pick')

    def test_switch_put(self):
        self.kardex.switch_put()
        self.assertEqual(self.kardex.mode, 'put')

    def test_switch_inventory(self):
        self.kardex.switch_inventory()
        self.assertEqual(self.kardex.mode, 'inventory')

    def test_pick_action_open_screen(self):
        self.kardex.switch_pick()
        action = self.kardex.action_open_screen()
        self.assertTrue(self.kardex.current_move_line)
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'stock.kardex')
        self.assertEqual(action['res_id'], self.kardex.id)

    def test_pick_select_next_move_line(self):
        self.kardex.switch_pick()
        self.kardex.select_next_move_line()
        self.assertEqual(self.kardex.current_move_line, self.out_move_line)
        self.assertEqual(self.kardex.operation_descr, _('Scan next PID'))

    def test_pick_save(self):
        self.kardex.switch_pick()
        self.kardex.current_move_line = self.out_move_line
        result = self.kardex.button_save()
        self.assertFalse(self.kardex.current_move_line)
        self.assertEqual(self.kardex.operation_descr, _('No operations'))
        expected_result = {
            'effect': {
                'fadeout': 'slow',
                'message': _('Congrats, you cleared the queue!'),
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
        self.assertEqual(result, expected_result)

    def test_on_barcode_scanned(self):
        # test to implement when the code is implemented
        with self.assertRaises(exceptions.UserError):
            self.kardex.on_barcode_scanned('foo')

    def test_button_release(self):
        # test to implement when the code is implemented
        with self.assertRaises(exceptions.UserError):
            self.kardex.button_release()

    def test_process_current_pick(self):
        self.kardex.switch_pick()
        self.kardex.current_move_line = self.out_move_line
        qty_to_process = self.out_move_line.product_qty
        self.kardex.process_current_pick()
        self.assertEqual(self.out_move_line.state, 'done')
        self.assertEqual(self.out_move_line.qty_done, qty_to_process)

    def test_process_current_put(self):
        # test to implement when the code is implemented
        with self.assertRaises(exceptions.UserError):
            self.kardex.process_current_put()

    def test_process_current_inventory(self):
        # test to implement when the code is implemented
        with self.assertRaises(exceptions.UserError):
            self.kardex.process_current_inventory()

    # TODO count move lines (need to create a few in different shuttles)
    # TODO test matrix
    # TODO test related fields
