from odoo.tests import Form

from .common import StockPickingProductInterchangeableCommon


class TestStockPicking(StockPickingProductInterchangeableCommon):
    def test_access_to_pass_interchangeable_field(self):
        """Test flow to show/hide pass_interchangeable field"""
        with self.assertRaises(AssertionError):
            with Form(self.env["stock.picking"]) as form:
                form.pass_interchangeable = True
        with self.assertRaises(AssertionError):
            with Form(self.env["stock.picking"]) as form:
                form.picking_type_id = self.picking_type_in
                form.pass_interchangeable = True
        with Form(self.env["stock.picking"]) as form:
            form.picking_type_id = self.picking_type_out
            form.pass_interchangeable = True
            self.assertTrue(
                form.pass_interchangeable,
                msg="'pass_interchangeable' field must be visible",
            )

    def _create_stock_picking(self, product_qty, pass_interchangeable=False):
        """
        Create stock picking
        :param int product_qty: Product Qty
        :param bool pass_interchangeable: Pass Interchangeable flag
        :return stock.picking: stock.picking record
        """
        form = Form(self.env["stock.picking"])
        form.partner_id = self.res_partner_bob
        form.picking_type_id = self.picking_type_out
        form.pass_interchangeable = pass_interchangeable
        with form.move_ids_without_package.new() as line:
            line.product_id = self.product_knife
            line.product_uom_qty = product_qty
        return form.save()

    def test_picking_note_for_interchangeable_products(self):
        """Test flow to create pickings note for interchangeable products"""
        expected_string = f"<b>{self.product_knife.display_name}</b> missing qty <i>27.0</i> was replaced with:<br>"  # noqa
        fork_str = f"<li><b>{self.product_fork.display_name}</b> <i>20.0</i></li>"
        spoon_str = f"<li><b>{self.product_spoon.display_name}</b> <i>7.0</i></li>"
        expected_string += f"<ul>{''.join([fork_str, spoon_str])}</ul><br>"
        picking = self._create_stock_picking(30)
        picking.action_confirm()
        self.assertEqual(
            str(picking.note), expected_string, msg="Strings must be the same"
        )

    def test_create_many_pickings(self):
        """Test flow to create and confirm pickings with different picking type"""
        picking_1 = self._create_stock_picking(30)
        form = Form(self.env["stock.picking"])
        form.picking_type_id = self.picking_type_in
        with form.move_ids_without_package.new() as line:
            line.product_id = self.product_napkin
            line.product_uom_qty = 10
        picking_2 = form.save()
        pickings = picking_1 | picking_2
        pickings.action_confirm()
        self.assertEqual(
            len(pickings.move_ids), 4, msg="Total stock moves count must be equal to 4"
        )
        self.assertEqual(
            len(picking_1.move_ids),
            3,
            msg="First picking moves count must be equal to 3",
        )
        self.assertEqual(
            len(picking_2.move_ids),
            1,
            msg="Second picking moves count must be equal to 1",
        )

    def test_create_delivery_stock_picking_with_pass_interchangeable(self):
        """Test flow to skip interchangeable behavior for delivery stock.picking record"""
        record = self._create_stock_picking(30, True)
        self.assertEqual(len(record.move_ids), 1, msg="Moves count must be equal to 1")
        knife_move = record.move_ids
        self.assertEqual(
            knife_move.product_id,
            self.product_knife,
            msg="Move product must be equal to 'Knife'",
        )
        self.assertEqual(
            knife_move.forecast_availability,
            -27,
            msg="Forecast Availability must be equal to -27",
        )
        self.assertEqual(
            knife_move.product_id.immediately_usable_qty,
            3,
            msg="Products count on hand must be equal to 3",
        )
        record.action_confirm()
        self.assertEqual(
            len(record.move_ids), 1, msg="Move lines count must be equal to 1"
        )
        knife_move = record.move_ids

        self.assertEqual(
            knife_move.product_id,
            self.product_knife,
            msg="Move product must be equal to 'Knife'",
        )
        self.assertEqual(
            knife_move.product_uom_qty, 30, msg="Move products Qty must be equal to 30"
        )

    def test_create_delivery_stock_picking_with_substitute_products_all_01(self):
        """Test flow to stock picking with substitute products 'all'"""
        record = self._create_stock_picking(30)
        self.assertEqual(len(record.move_ids), 1, msg="Moves count must be equal to 1")
        knife_move = record.move_ids
        self.assertEqual(
            knife_move.product_id,
            self.product_knife,
            msg="Move product must be equal to 'Knife'",
        )
        self.assertEqual(
            knife_move.forecast_availability,
            -27,
            msg="Forecast Availability must be equal to -27",
        )
        self.assertEqual(
            knife_move.product_id.immediately_usable_qty,
            3,
            msg="Products count on hand must be equal to 3",
        )
        record.action_confirm()
        self.assertEqual(len(record.move_ids), 3, msg="Moves count must be equal to 3")
        knife_move, fork_move, spoon_move = record.move_ids

        self.assertEqual(
            knife_move.product_id,
            self.product_knife,
            msg="Move product must be equal to 'Knife'",
        )
        self.assertEqual(
            knife_move.product_uom_qty, 3, msg="Move products Qty must be equal to 3"
        )

        self.assertEqual(
            fork_move.product_id,
            self.product_fork,
            msg="Move product must be equal to 'Fork'",
        )
        self.assertEqual(
            fork_move.product_uom_qty, 20, msg="Move products Qty must be equal to 20"
        )

        self.assertEqual(
            spoon_move.product_id,
            self.product_spoon,
            msg="Move product must be equal to 'Spoon'",
        )
        self.assertEqual(
            spoon_move.product_uom_qty, 7, msg="Move products Qty must be equal to 7"
        )

    def test_create_delivery_stock_picking_with_substitute_products_all_02(self):
        """Test flow to stock picking with substitute products 'all'"""
        record = self._create_stock_picking(32)
        self.assertEqual(len(record.move_ids), 1, msg="Moves count must be equal to 1")
        knife_move = record.move_ids
        self.assertEqual(
            knife_move.product_id,
            self.product_knife,
            msg="Move product must be equal to 'Knife'",
        )
        self.assertEqual(
            knife_move.forecast_availability,
            -29,
            msg="Forecast Availability must be equal to -29",
        )
        self.assertEqual(
            knife_move.product_id.immediately_usable_qty,
            3,
            msg="Products count on hand must be equal to 3",
        )
        record.action_confirm()
        self.assertEqual(len(record.move_ids), 1, msg="Moves count must be equal to 1")
        knife_move = record.move_ids

        self.assertEqual(
            knife_move.product_id,
            self.product_knife,
            msg="Move product must be equal to 'Knife'",
        )
        self.assertEqual(
            knife_move.product_uom_qty, 32, msg="Move products Qty must be equal to 32"
        )

    def test_create_delivery_stock_picking_with_substitute_products_any(self):
        """Test flow to stock picking with substitute products 'any'"""
        self.picking_type_out.write({"substitute_products_mode": "any"})
        record = self._create_stock_picking(32)
        self.assertEqual(len(record.move_ids), 1, msg="Moves count must be equal to 1")
        knife_move = record.move_ids
        self.assertEqual(
            knife_move.product_id,
            self.product_knife,
            msg="Move product must be equal to 'Knife'",
        )
        self.assertEqual(
            knife_move.forecast_availability,
            -29,
            msg="Forecast Availability must be equal to -29",
        )
        self.assertEqual(
            knife_move.product_id.immediately_usable_qty,
            3,
            msg="Products count on hand must be equal to 3",
        )
        record.action_confirm()
        self.assertEqual(len(record.move_ids), 3, msg="Moves count must be equal to 3")
        knife_move, fork_move, spoon_move = record.move_ids

        self.assertEqual(
            knife_move.product_id,
            self.product_knife,
            msg="Move product must be equal to 'Knife'",
        )
        self.assertEqual(
            knife_move.product_uom_qty, 4, msg="Move products Qty must be equal to 4"
        )

        self.assertEqual(fork_move.product_id, self.product_fork)
        self.assertEqual(
            fork_move.product_uom_qty, 20, msg="Move products Qty must be equal to 20"
        )

        self.assertEqual(spoon_move.product_id, self.product_spoon)
        self.assertEqual(
            spoon_move.product_uom_qty, 8, msg="Move products Qty must be equal to 8"
        )
