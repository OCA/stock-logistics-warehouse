# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unittest

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
        self.assertEqual(self.kardex.current_move_line_id, self.out_move_line)

    def test_switch_put(self):
        self.kardex.switch_put()
        self.assertEqual(self.kardex.mode, 'put')
        # TODO check that we have an incoming move when switching
        self.assertEqual(
            self.kardex.current_move_line_id,
            self.env['stock.move.line'].browse(),
        )

    def test_switch_inventory(self):
        self.kardex.switch_inventory()
        self.assertEqual(self.kardex.mode, 'inventory')
        # TODO check that we have what we should (what?)
        self.assertEqual(
            self.kardex.current_move_line_id,
            self.env['stock.move.line'].browse(),
        )

    def test_pick_action_open_screen(self):
        self.kardex.switch_pick()
        action = self.kardex.action_open_screen()
        self.assertTrue(self.kardex.current_move_line_id)
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'stock.kardex')
        self.assertEqual(action['res_id'], self.kardex.id)

    def test_pick_select_next_move_line(self):
        self.kardex.switch_pick()
        self.kardex.select_next_move_line()
        self.assertEqual(self.kardex.current_move_line_id, self.out_move_line)
        self.assertEqual(self.kardex.operation_descr, _('Scan next PID'))

    def test_pick_save(self):
        self.kardex.switch_pick()
        self.kardex.current_move_line_id = self.out_move_line
        result = self.kardex.button_save()
        self.assertFalse(self.kardex.current_move_line_id)
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

    def test_pick_related_fields(self):
        self.kardex.switch_pick()
        ml = self.kardex.current_move_line_id = self.out_move_line

        # Kardex trays related fields
        # For pick, this is the source location, which is the cell where the
        # product is.
        self.assertEqual(self.kardex.kardex_tray_location_id, ml.location_id)
        self.assertEqual(self.kardex.kardex_tray_name, ml.location_id.name)
        self.assertEqual(
            self.kardex.kardex_tray_type_id,
            # the tray type is on the parent of the cell (on the tray)
            ml.location_id.location_id.kardex_tray_type_id,
        )
        self.assertEqual(
            self.kardex.kardex_tray_type_code,
            ml.location_id.location_id.kardex_tray_type_id.code,
        )
        self.assertEqual(self.kardex.kardex_tray_x, ml.location_id.posx)
        self.assertEqual(self.kardex.kardex_tray_y, ml.location_id.posy)

        # Move line related fields
        self.assertEqual(self.kardex.picking_id, ml.picking_id)
        self.assertEqual(self.kardex.product_id, ml.product_id)
        self.assertEqual(self.kardex.product_uom_id, ml.product_uom_id)
        self.assertEqual(self.kardex.product_uom_qty, ml.product_uom_qty)
        self.assertEqual(self.kardex.qty_done, ml.qty_done)
        self.assertEqual(self.kardex.lot_id, ml.lot_id)

    def test_pick_count_move_lines(self):
        product1 = self.env.ref('stock_kardex.product_running_socks')
        product2 = self.env.ref('stock_kardex.product_recovery_socks')
        # cancel the picking from demo data to start from a clean state
        self.env.ref(
            'stock_kardex.stock_picking_out_demo_kardex_1'
        ).action_cancel()

        # ensure that we have stock in some cells, we'll put product1
        # in the first kardex and product2 in the second
        cell1 = self.env.ref(
            'stock_kardex.stock_location_kardex_demo_tray_1a_x3y2'
        )
        self._update_quantity_in_cell(cell1, product1, 50)
        cell2 = self.env.ref(
            'stock_kardex.stock_location_kardex_demo_tray_2a_x1y1'
        )
        self._update_quantity_in_cell(cell2, product2, 50)

        # create pickings (we already have an existing one from demo data)
        pickings = self.env['stock.picking'].browse()
        pickings |= self._create_simple_picking_out(product1, 1)
        pickings |= self._create_simple_picking_out(product1, 1)
        pickings |= self._create_simple_picking_out(product1, 1)
        pickings |= self._create_simple_picking_out(product1, 1)
        pickings |= self._create_simple_picking_out(product2, 20)
        pickings |= self._create_simple_picking_out(product2, 30)
        # this one should be 'assigned', so should be included in the operation
        # count
        unassigned = self._create_simple_picking_out(product2, 1)
        pickings |= unassigned
        pickings.action_confirm()
        # product1 will be taken from the kardex1, product2 from kardex2
        pickings.action_assign()

        kardex1 = self.kardex
        kardex2 = self.env.ref('stock_kardex.stock_kardex_demo_shuttle_2')

        self.assertEqual(kardex1.number_of_ops, 4)
        self.assertEqual(kardex2.number_of_ops, 2)
        self.assertEqual(kardex1.number_of_ops_all, 6)
        self.assertEqual(kardex2.number_of_ops_all, 6)

        # Process a line, should change the numbers.
        kardex1.select_next_move_line()
        kardex1.process_current_pick()
        self.assertEqual(kardex1.number_of_ops, 3)
        self.assertEqual(kardex2.number_of_ops, 2)
        self.assertEqual(kardex1.number_of_ops_all, 5)
        self.assertEqual(kardex2.number_of_ops_all, 5)

        # add stock and make the last one assigned to check the number is updated
        self._update_quantity_in_cell(cell2, product2, 10)
        unassigned.action_assign()
        self.assertEqual(kardex1.number_of_ops, 3)
        self.assertEqual(kardex2.number_of_ops, 3)
        self.assertEqual(kardex1.number_of_ops_all, 6)
        self.assertEqual(kardex2.number_of_ops_all, 6)

    @unittest.skip('Not implemented')
    def test_put_count_move_lines(self):
        pass

    @unittest.skip('Not implemented')
    def test_inventory_count_move_lines(self):
        pass

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
        self.kardex.current_move_line_id = self.out_move_line
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

    def test_matrix(self):
        self.kardex.switch_pick()
        self.kardex.current_move_line_id = self.out_move_line
        location = self.out_move_line.location_id
        # offset by -1 because the fields are for humans
        expected_x = location.posx - 1
        expected_y = location.posy - 1
        self.assertEqual(
            self.kardex.kardex_tray_matrix,
            {
                'selected': [expected_x, expected_y],
                # fmt: off
                'cells': [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0, 0, 0, 0],
                ]
                # fmt: on
            },
        )
