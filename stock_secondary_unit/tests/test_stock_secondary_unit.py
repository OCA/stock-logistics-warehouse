# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class TestProductSecondaryUnit(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Active multiple units of measure security group for user
        cls.env.user.groups_id = [(4, cls.env.ref("uom.group_uom").id)]
        cls.StockPicking = cls.env["stock.picking"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.show_operations = True

        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_ton = cls.env.ref("uom.product_uom_ton")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        ProductAttribute = cls.env["product.attribute"]
        ProductAttributeValue = cls.env["product.attribute.value"]
        cls.attribute_color = ProductAttribute.create({"name": "test_color"})
        cls.attribute_value_white = ProductAttributeValue.create(
            {"name": "test_white", "attribute_id": cls.attribute_color.id}
        )
        cls.attribute_value_black = ProductAttributeValue.create(
            {"name": "test_black", "attribute_id": cls.attribute_color.id}
        )
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "type": "consu",
                "is_storable": True,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "code": "A",
                            "name": "unit-500",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        },
                    ),
                    Command.create(
                        {
                            "code": "B",
                            "name": "unit-900",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.9,
                        },
                    ),
                    Command.create(
                        {
                            "code": "C",
                            "name": "box 10",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 10,
                        },
                    ),
                ],
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attribute_color.id,
                            "value_ids": [
                                (4, cls.attribute_value_white.id),
                                (4, cls.attribute_value_black.id),
                            ],
                        },
                    )
                ],
            }
        )
        secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product_template.id)], limit=1
        )
        cls.product_template.product_variant_ids.write(
            {"stock_secondary_uom_id": secondary_unit.id}
        )
        StockQuant = cls.env["stock.quant"]
        cls.quant_white = StockQuant.create(
            {
                "product_id": cls.product_template.product_variant_ids[0].id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )
        cls.quant_black = StockQuant.create(
            {
                "product_id": cls.product_template.product_variant_ids[1].id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )

    def test_01_stock_secondary_unit_template(self):
        self.assertEqual(self.product_template.secondary_unit_qty_available, 0)

    def test_02_stock_secondary_unit_variant(self):
        for variant in self.product_template.product_variant_ids.filtered(
            "product_template_attribute_value_ids"
        ):
            self.assertEqual(variant.secondary_unit_qty_available, 20)

    def test_03_stock_picking_secondary_unit(self):
        StockPicking = self.env["stock.picking"]
        product1 = self.product_template.product_variant_ids[0]
        move_vals = {
            "product_id": product1.id,
            "name": product1.display_name,
            "secondary_uom_id": product1.product_tmpl_id.secondary_uom_ids[0].id,
            "product_uom": product1.uom_id.id,
            "product_uom_qty": 10.0,
            "location_id": self.location_supplier.id,
            "location_dest_id": self.location_stock.id,
        }
        do_vals = {
            "location_id": self.location_supplier.id,
            "location_dest_id": self.location_stock.id,
            "picking_type_id": self.picking_type_in.id,
            "move_ids_without_package": [
                (0, None, move_vals),
                (0, None, move_vals),
            ],  # 2 moves
        }
        delivery_order = StockPicking.create(do_vals)
        delivery_order.action_confirm()
        # Move is merged into 1 line for both stock.move and stock.move.line
        self.assertEqual(len(delivery_order.move_ids), 1)
        self.assertEqual(len(delivery_order.move_line_ids), 1)
        # Qty merged to 20, and secondary unit qty is 40line
        uom_qty = sum(delivery_order.move_ids.mapped("product_uom_qty"))
        secondary_uom_qty = sum(
            delivery_order.move_line_ids.mapped("secondary_uom_qty")
        )
        self.assertEqual(uom_qty, 20.0)
        self.assertEqual(secondary_uom_qty, 40.0)

    def test_picking_secondary_unit(self):
        product = self.product_template.product_variant_ids[0]
        with Form(
            self.StockPicking.with_context(
                planned_picking=True,
                default_picking_type_id=self.picking_type_out.id,
            )
        ) as picking_form:
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
                self.assertEqual(move.product_uom_qty, 0.5)
                move.secondary_uom_qty = 2
                self.assertEqual(move.product_uom_qty, 1)
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[1]
                self.assertEqual(move.product_uom_qty, 1.8)
                move.product_uom_qty = 5
                self.assertAlmostEqual(move.secondary_uom_qty, 5.56, 2)
                # Change uom from stock move line
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[2]
                self.assertEqual(move.product_uom_qty, 10)
                move.product_uom = self.product_uom_ton
                self.assertAlmostEqual(move.secondary_uom_qty, 1000, 2)

        picking = picking_form.save()
        picking.action_confirm()
        stock_move_line = picking.move_line_ids_without_package
        stock_move_line.product_id = product
        stock_move_line.product_uom_id = stock_move_line.product_id.uom_id.id
        stock_move_line.secondary_uom_qty = 1
        stock_move_line.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
        self.assertEqual(stock_move_line.quantity, 0.5)
        stock_move_line.secondary_uom_qty = 2
        self.assertEqual(stock_move_line.quantity, 1)
        stock_move_line.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[1]
        self.assertEqual(stock_move_line.quantity, 1.8)
        stock_move_line.quantity = 5
        self.assertAlmostEqual(stock_move_line.secondary_uom_qty, 5.56, 2)

    def test_secondary_unit_merge_move_diff_uom(self):
        product = self.product_template.product_variant_ids[0]
        with Form(
            self.StockPicking.with_context(
                planned_picking=True,
                default_picking_type_id=self.picking_type_out.id,
            )
        ) as picking_form:
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[1]
        picking = picking_form.save()
        picking.action_confirm()
        self.assertEqual(len(picking.move_ids), 2)

    def test_backorder_secondary_unit_independent(self):
        """An "independent" secondary unit (e.g. pieces vs. weight) must be
        split as an exact count on a backorder, never recomputed
        proportionally from the primary quantity (e.g. weight): 40 pieces
        demanded (28 kg theoretical), only 30 actually picked, weighing 22
        kg (not the 21 kg theoretical for 30 pieces) -> the backorder must
        be for exactly 10 pieces, not a weight-based estimate.
        """
        product = self.product_template.product_variant_ids[0]
        secondary_unit = self.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "code": "PZ",
                "name": "piece",
                "uom_id": self.product_uom_unit.id,
                "factor": 0.7,
                "dependency_type": "independent",
            }
        )
        picking = self.StockPicking.create(
            {
                "location_id": self.location_supplier.id,
                "location_dest_id": self.location_stock.id,
                "picking_type_id": self.picking_type_in.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "name": product.display_name,
                            "secondary_uom_id": secondary_unit.id,
                            "secondary_uom_qty": 40.0,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 28.0,
                            "location_id": self.location_supplier.id,
                            "location_dest_id": self.location_stock.id,
                        }
                    ),
                ],
            }
        )
        picking.action_confirm()
        move_line = picking.move_line_ids
        # Weigh 22 kg (less than the 28 kg demanded, so a backorder is
        # created) but only actually count 30 of the 40 pieces demanded
        move_line.quantity = 22.0
        move_line.secondary_uom_qty = 30.0
        action = picking.button_validate()
        if isinstance(action, dict):
            wizard = Form(
                self.env[action["res_model"]].with_context(**action["context"])
            ).save()
            wizard.process()
        backorder = self.StockPicking.search([("backorder_id", "=", picking.id)])
        self.assertTrue(backorder)
        self.assertEqual(picking.move_ids.secondary_uom_qty, 30.0)
        self.assertEqual(picking.move_ids.product_uom_qty, 22.0)
        self.assertEqual(backorder.move_ids.secondary_uom_qty, 10.0)

    def test_secondary_uom_qty_done(self):
        """secondary_uom_qty_done mirrors `quantity` (the primary done
        aggregate, computed from move_line_ids.quantity) - it must reflect
        what's actually counted on the lines regardless of the move's own
        demand, and follow the lines live as they change.
        """
        product = self.product_template.product_variant_ids[0]
        secondary_unit = self.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "code": "PZ",
                "name": "piece",
                "uom_id": self.product_uom_unit.id,
                "factor": 0.7,
                "dependency_type": "secondary_priority",
            }
        )
        move = self.env["stock.move"].create(
            {
                "product_id": product.id,
                "name": product.display_name,
                "secondary_uom_id": secondary_unit.id,
                "secondary_uom_qty": 40.0,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 28.0,
                "location_id": self.location_supplier.id,
                "location_dest_id": self.location_stock.id,
            }
        )
        self.assertEqual(move.secondary_uom_qty_done, 0.0)
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.secondary_uom_qty = 30.0
        self.assertEqual(move.secondary_uom_qty_done, 30.0)
        # The demand is untouched - only the done aggregate follows the line.
        self.assertEqual(move.secondary_uom_qty, 40.0)

    def test_backorder_secondary_unit_secondary_priority(self):
        """ "secondary_priority" behaves like "dependent" for estimating the
        primary quantity (weight) from the secondary one (pieces) at
        creation time, but like "independent" for never recomputing pieces
        back from weight - including on a backorder split, where a naive
        write would otherwise retrigger the primary-from-secondary compute
        and clobber the real measured weight with a theoretical estimate.
        """
        product = self.product_template.product_variant_ids[0]
        secondary_unit = self.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "code": "PZ",
                "name": "piece",
                "uom_id": self.product_uom_unit.id,
                "factor": 0.7,
                "dependency_type": "secondary_priority",
            }
        )
        picking = self.StockPicking.create(
            {
                "location_id": self.location_supplier.id,
                "location_dest_id": self.location_stock.id,
                "picking_type_id": self.picking_type_in.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "name": product.display_name,
                            "secondary_uom_id": secondary_unit.id,
                            "product_uom": product.uom_id.id,
                            "location_id": self.location_supplier.id,
                            "location_dest_id": self.location_stock.id,
                        }
                    ),
                ],
            }
        )
        # Setting the piece count auto-estimates the weight demand (40 *
        # 0.7), unlike "independent" which would have left it at 0. Set via
        # write() (a normal onchange/UI-driven update), not in the create()
        # vals above, since precompute doesn't reliably chain two
        # interdependent computed fields given in the same create() call.
        picking.move_ids.secondary_uom_qty = 40.0
        self.assertEqual(picking.move_ids.product_uom_qty, 28.0)
        picking.action_confirm()
        move_line = picking.move_line_ids
        # Weigh 22 kg (less than the 28 kg demanded, so a backorder is
        # created) but only actually count 30 of the 40 pieces demanded
        move_line.quantity = 22.0
        move_line.secondary_uom_qty = 30.0
        action = picking.button_validate()
        if isinstance(action, dict):
            wizard = Form(
                self.env[action["res_model"]].with_context(**action["context"])
            ).save()
            wizard.process()
        backorder = self.StockPicking.search([("backorder_id", "=", picking.id)])
        self.assertTrue(backorder)
        self.assertEqual(picking.move_ids.secondary_uom_qty, 30.0)
        # The real measured weight (22 kg) must survive the split, not get
        # overwritten by the theoretical 30 * 0.7 = 21 kg estimate.
        self.assertEqual(picking.move_ids.product_uom_qty, 22.0)
        self.assertEqual(backorder.move_ids.secondary_uom_qty, 10.0)

    def _create_pick_ship_pick(self):
        """Set up a "pick_ship" warehouse and return a reserved pick of
        28 kg / 40 pieces for a count-preserving secondary unit.
        """
        self.warehouse.delivery_steps = "pick_ship"
        pick_type = self.warehouse.pick_type_id
        product = self.product_template.product_variant_ids[0]
        secondary_unit = self.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "code": "PZ",
                "name": "piece",
                "uom_id": self.product_uom_unit.id,
                "factor": 0.7,
                "dependency_type": "secondary_priority",
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            product, pick_type.default_location_src_id, 28.0
        )
        pick = self.StockPicking.create(
            {
                "picking_type_id": pick_type.id,
                "location_id": pick_type.default_location_src_id.id,
                "location_dest_id": pick_type.default_location_dest_id.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "name": product.display_name,
                            "secondary_uom_id": secondary_unit.id,
                            "secondary_uom_qty": 40.0,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 28.0,
                            "location_id": pick_type.default_location_src_id.id,
                            "location_dest_id": pick_type.default_location_dest_id.id,
                        }
                    ),
                ],
            }
        )
        pick.action_confirm()
        pick.action_assign()
        return pick

    def test_pick_ship_route_secondary_priority_survives_push_and_merge(self):
        """A "pick_ship" delivery route is pull (SO -> pick) + PUSH
        (pick -> ship), not a chain of pull rules: the ship move doesn't
        exist until the pick is validated, at which point core creates it
        via `copy()`. secondary_uom_qty has copy=False, so without a fix
        the ship move starts at 0 pieces and a weight-based fallback
        estimate fills it in - wrong, and then a second backorder pick's
        push gets silently discarded by core's move merge, which only
        knows how to sum product_uom_qty. Reproduces a real bug: an
        outgoing delivery ended up with the right kg but the wrong (or
        entirely lost) piece count after a backorder was created one step
        upstream during picking.
        """
        pick = self._create_pick_ship_pick()
        pick_move_line = pick.move_line_ids
        # Weigh 22 kg but only actually count 30 of the 40 pieces demanded
        pick_move_line.quantity = 22.0
        pick_move_line.secondary_uom_qty = 30.0
        pick.move_ids.picked = True
        action = pick.button_validate()
        if isinstance(action, dict):
            wizard = Form(
                self.env[action["res_model"]].with_context(**action["context"])
            ).save()
            wizard.process()
        pick_backorder = self.StockPicking.search([("backorder_id", "=", pick.id)])
        self.assertTrue(pick_backorder)

        ship_move = pick.move_ids.move_dest_ids
        self.assertTrue(ship_move, "The push rule should have created the ship move")
        self.assertEqual(ship_move.product_uom_qty, 22.0)
        # The pushed move must carry the real counted pieces, not a
        # weight-based estimate (22 / 0.7 = 31.43, which is what the old
        # fallback would have produced).
        self.assertEqual(ship_move.secondary_uom_qty, 30.0)

        # Now validate the backorder pick too: its push creates a second
        # ship move that core merges into the first one.
        backorder_move_line = pick_backorder.move_line_ids
        backorder_move_line.quantity = 6.0
        backorder_move_line.secondary_uom_qty = 10.0
        pick_backorder.move_ids.picked = True
        pick_backorder.button_validate()

        self.assertEqual(len(ship_move.exists()), 1)
        self.assertEqual(ship_move.product_uom_qty, 28.0)
        self.assertEqual(
            ship_move.move_orig_ids, pick.move_ids | pick_backorder.move_ids
        )
        # The merge must add the backorder's pieces too, not just its kg.
        self.assertEqual(ship_move.secondary_uom_qty, 40.0)

    def test_pick_ship_route_secondary_priority_no_backorder(self):
        """Same push route, but the user finalizes the partial pick with
        "No Backorder": the 10 uncounted pieces are never coming, and no
        split ever happens. Core leaves the pick move permanently short
        (demand 28 kg, only 22 kg done) instead of reducing its demand,
        so the move also keeps demanding the original 40 pieces - and
        pushing THAT to the ship move would send downstream a piece count
        that never physically existed. The pushed move must carry what
        was actually counted (30 pieces for 22 kg), exactly like core
        pushes the done quantity rather than the demand.
        """
        pick = self._create_pick_ship_pick()
        pick_move_line = pick.move_line_ids
        # Weigh 22 kg but only actually count 30 of the 40 pieces demanded
        pick_move_line.quantity = 22.0
        pick_move_line.secondary_uom_qty = 30.0
        pick.move_ids.picked = True
        action = pick.button_validate()
        self.assertIsInstance(action, dict)
        wizard = Form(self.env[action["res_model"]].with_context(**action["context"]))
        wizard.save().process_cancel_backorder()

        self.assertFalse(self.StockPicking.search([("backorder_id", "=", pick.id)]))
        # Core's own semantics for a cancelled backorder: the demand is
        # NOT reduced to what was done, the shortfall stays visible. The
        # secondary unit follows it instead of inventing an asymmetry.
        self.assertEqual(pick.move_ids.product_uom_qty, 28.0)
        self.assertEqual(pick.move_ids.secondary_uom_qty, 40.0)
        self.assertEqual(pick.move_ids.quantity, 22.0)

        ship_move = pick.move_ids.move_dest_ids
        self.assertTrue(ship_move, "The push rule should have created the ship move")
        self.assertEqual(ship_move.product_uom_qty, 22.0)
        # 30 counted pieces, not the pick's stale 40-piece demand.
        self.assertEqual(ship_move.secondary_uom_qty, 30.0)

    def test_pick_ship_route_secondary_priority_uncounted(self):
        """The whole demand is processed straight from the reservation
        without the operator ever touching the piece count, so the move
        lines carry no count at all. There is nothing measured to push,
        so the pushed move falls back to the demand (40 pieces for the
        full 28 kg) rather than shipping zero pieces.
        """
        pick = self._create_pick_ship_pick()
        self.assertEqual(pick.move_line_ids.quantity, 28.0)
        self.assertEqual(pick.move_line_ids.secondary_uom_qty, 0.0)
        self.assertTrue(pick.button_validate())

        ship_move = pick.move_ids.move_dest_ids
        self.assertTrue(ship_move, "The push rule should have created the ship move")
        self.assertEqual(ship_move.product_uom_qty, 28.0)
        self.assertEqual(ship_move.secondary_uom_qty, 40.0)

    def test_secondary_unit_merge_move_same_uom(self):
        product = self.product_template.product_variant_ids[0]
        with Form(
            self.StockPicking.with_context(
                planned_picking=True,
                default_picking_type_id=self.picking_type_out.id,
            )
        ) as picking_form:
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
        picking = picking_form.save()
        picking.action_confirm()
        self.assertEqual(len(picking.move_ids), 1)
        self.assertEqual(picking.move_ids.secondary_uom_qty, 2)
