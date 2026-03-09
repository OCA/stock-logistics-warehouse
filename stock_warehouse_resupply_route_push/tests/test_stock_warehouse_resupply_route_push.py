# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestWarehouseResupplyRoutePush(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh_0 = cls.env.ref("stock.warehouse0")
        cls.company_2 = cls.env["res.company"].create({"name": "Test company 2"})
        cls.partner_wh1 = cls.env["res.partner"].create({"name": "WH1"})
        cls.partner_wh2 = cls.env["res.partner"].create({"name": "WH2"})
        cls.partner_wh5 = cls.env["res.partner"].create({"name": "WH5"})
        cls.wh_comp_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Test WH company 2",
                "code": "WHC2",
                "company_id": cls.company_2.id,
            }
        )
        cls.wh_1 = cls.env["stock.warehouse"].create(
            {"name": "Test WH 1", "code": "WH1", "partner_id": cls.partner_wh1.id}
        )
        cls.wh_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Test WH 2",
                "code": "WH2",
                "partner_id": cls.partner_wh2.id,
                "resupply_wh_push": True,
                "resupply_wh_ids": [(6, 0, [cls.wh_1.id])],
            }
        )
        cls.wh_5 = cls.env["stock.warehouse"].create(
            {
                "name": "Test WH 5",
                "code": "WH5",
                "partner_id": cls.partner_wh5.id,
                "resupply_wh_push": True,
                "resupply_wh_ids": [(6, 0, [cls.wh_1.id])],
            }
        )
        cls.route_wh_1_to_wh_2 = cls.wh_2.resupply_route_ids
        cls.route_wh_1_to_wh_5 = cls.wh_5.resupply_route_ids
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "is_storable": True,
                "route_ids": [
                    (6, 0, [cls.route_wh_1_to_wh_2.id, cls.route_wh_1_to_wh_5.id])
                ],
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.wh_1.lot_stock_id,
            10,
        )
        cls.category = cls.env["product.category"].create({"name": "Test Category"})
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test product 2",
                "is_storable": True,
                "categ_id": cls.category.id,
            }
        )

    def _run_procurement(self, product, wh, qty):
        moves_before = self.env["stock.move"].search([])
        proc_group = self.env["procurement.group"]
        uom = product.uom_id
        proc_qty, proc_uom = uom._adjust_uom_quantities(qty, uom)
        today = fields.Date.today()
        proc_group = self.env["procurement.group"].create({})
        values = {
            "group_id": proc_group,
            "date_planned": today,
            "date_deadline": today,
            "warehouse_id": wh or False,
            "company_id": self.company,
        }
        procurement = proc_group.Procurement(
            product,
            proc_qty,
            proc_uom,
            wh.lot_stock_id,
            product.name,
            "procure test",
            self.company,
            values,
        )
        proc_group.run([procurement])
        moves_after = self.env["stock.move"].search([])
        return moves_after - moves_before

    def _validate_picking(self, picking):
        picking.move_line_ids.write({"picked": True})
        picking._action_done()

    def test_01_resupply_from_wh_push(self):
        """Test inter-warehouse with push option enabled."""
        moves = self._run_procurement(self.product, self.wh_2, 10)
        # We expect only the delivery from wh 1 to wh 2.
        self.assertEqual(len(moves), 1)
        delivery_from_wh_1 = moves
        self.assertEqual(delivery_from_wh_1.picking_type_id.code, "outgoing")
        self.assertEqual(
            delivery_from_wh_1.picking_type_id, self.wh_1.out_inter_wh_internal_type_id
        )
        self.assertEqual(delivery_from_wh_1.location_dest_id.usage, "transit")
        # Validating the first move create the next one
        self._validate_picking(delivery_from_wh_1.picking_id)
        self.assertEqual(delivery_from_wh_1.state, "done")
        receipt_at_wh_2 = delivery_from_wh_1.move_dest_ids
        self.assertEqual(len(receipt_at_wh_2), 1)
        self.assertEqual(receipt_at_wh_2.state, "assigned")
        self.assertEqual(receipt_at_wh_2.picking_type_id, self.wh_2.in_type_id)
        self.assertEqual(
            delivery_from_wh_1.location_dest_id, receipt_at_wh_2.location_id
        )
        self._validate_picking(receipt_at_wh_2.picking_id)
        self.assertEqual(receipt_at_wh_2.state, "done")

    def test_02_resupply_from_wh_pull(self):
        """Test inter-warehouse with pull option, standard behavior."""
        # Disable push option and recreate routes.
        self.wh_2.write({"resupply_wh_push": False})
        self.wh_2.action_recreate_resupply_routes()
        self.assertFalse(self.route_wh_1_to_wh_2.active)
        new_resupply_route = self.wh_2.resupply_route_ids
        self.assertTrue(new_resupply_route.active)
        moves = self._run_procurement(self.product, self.wh_2, 10)
        # We expect both the delivery from wh 1 and the receipt at wh 2.
        self.assertEqual(len(moves), 2)
        receipt_at_wh_2, delivery_from_wh_1 = moves
        self.assertEqual(delivery_from_wh_1.picking_type_id.code, "outgoing")
        self.assertEqual(delivery_from_wh_1.picking_type_id, self.wh_1.out_type_id)
        self.assertEqual(delivery_from_wh_1.location_dest_id.usage, "transit")
        # Validating the first move to process second one.
        self.assertEqual(receipt_at_wh_2.state, "waiting")
        self._validate_picking(delivery_from_wh_1.picking_id)
        self.assertEqual(delivery_from_wh_1.state, "done")
        self.assertEqual(receipt_at_wh_2.state, "assigned")
        self.assertEqual(receipt_at_wh_2.picking_type_id, self.wh_2.in_type_id)
        self.assertEqual(
            delivery_from_wh_1.location_dest_id, receipt_at_wh_2.location_id
        )
        self._validate_picking(receipt_at_wh_2.picking_id)
        self.assertEqual(receipt_at_wh_2.state, "done")

    def test_03_resupply_from_wh_push_and_3_steps(self):
        """Test inter-warehouse with 3 steps delivery in the source wh and push
        option enabled for inter-warehouse."""
        # Enable 3 steps in wh 1 and recreate routes in wh 2.
        # In inter-warehouse it doesn't matter 2 or 3 steps, it will always be a
        # 2-step delivery from the supplier warehouse. This is standard Odoo behavior.
        self.wh_1.write(
            {
                "delivery_steps": "pick_pack_ship",
            }
        )
        # Note that this manual recreation is needed and does not even happen in
        # standard Odoo with standard routes.
        self.wh_2.action_recreate_resupply_routes()
        self.assertFalse(self.route_wh_1_to_wh_2.active)
        new_resupply_route = self.wh_2.resupply_route_ids
        self.assertTrue(new_resupply_route.active)
        moves = self._run_procurement(self.product, self.wh_2, 10)
        # As mentioned above, we expect the pick operation and the delivery from wh 1.
        self.assertEqual(len(moves), 2)
        delivery_from_wh_1, pick_in_wh_1 = moves
        self.assertEqual(pick_in_wh_1.picking_type_id.code, "internal")
        self.assertEqual(pick_in_wh_1.location_id, self.wh_1.lot_stock_id)
        self.assertEqual(
            pick_in_wh_1.location_dest_id, self.wh_1.wh_output_stock_loc_id
        )
        self.assertEqual(delivery_from_wh_1.state, "waiting")
        self.assertEqual(pick_in_wh_1.move_dest_ids, delivery_from_wh_1)
        self.assertEqual(delivery_from_wh_1.picking_type_id.code, "outgoing")
        self.assertEqual(
            delivery_from_wh_1.picking_type_id, self.wh_1.out_inter_wh_internal_type_id
        )
        self.assertEqual(
            delivery_from_wh_1.location_id, self.wh_1.wh_output_stock_loc_id
        )
        self.assertEqual(delivery_from_wh_1.location_dest_id.usage, "transit")
        # Validating the first 2 steps will generate the receipt at the supplied wh.
        self._validate_picking(pick_in_wh_1.picking_id)
        self.assertEqual(pick_in_wh_1.state, "done")
        self.assertEqual(delivery_from_wh_1.state, "assigned")
        self._validate_picking(delivery_from_wh_1.picking_id)
        self.assertEqual(delivery_from_wh_1.state, "done")
        receipt_at_wh_2 = delivery_from_wh_1.move_dest_ids
        self.assertEqual(len(receipt_at_wh_2), 1)
        self.assertEqual(receipt_at_wh_2.state, "assigned")
        self.assertEqual(receipt_at_wh_2.picking_type_id, self.wh_2.in_type_id)
        self.assertEqual(
            delivery_from_wh_1.location_dest_id, receipt_at_wh_2.location_id
        )
        self._validate_picking(receipt_at_wh_2.picking_id)
        self.assertEqual(receipt_at_wh_2.state, "done")

    def test_04_resupply_from_wh_pull_and_3_steps(self):
        """Test inter-warehouse with 3 steps delivery in the source wh and pull
        option enabled for inter-warehouse, standard behavior."""
        # Disable push option and recreate routes.
        self.wh_2.write({"resupply_wh_push": False})
        # In inter-warehouse it doesn't matter 2 or 3 steps, it will always be a
        # 2-step delivery from the supplier warehouse. This is standard Odoo behavior.
        self.wh_1.write(
            {
                "delivery_steps": "pick_pack_ship",
            }
        )
        # Note that this manual recreation is needed and does not even happen in
        # standard Odoo with standard routes.
        self.wh_2.action_recreate_resupply_routes()
        self.assertFalse(self.route_wh_1_to_wh_2.active)
        new_resupply_route = self.wh_2.resupply_route_ids
        self.assertTrue(new_resupply_route.active)
        moves = self._run_procurement(self.product, self.wh_2, 10)
        # As mentioned above, we expect the pick operation and the delivery
        # from wh 1 and the receipt at wh 2.
        self.assertEqual(len(moves), 3)
        receipt_at_wh_2, delivery_from_wh_1, pick_in_wh_1 = moves
        self.assertEqual(pick_in_wh_1.picking_type_id.code, "internal")
        self.assertEqual(pick_in_wh_1.location_id, self.wh_1.lot_stock_id)
        # This is sending first to pack location and not to output. It
        # doesn't make sense, but it is the standard Odoo behavior...
        self.assertEqual(pick_in_wh_1.location_dest_id, self.wh_1.wh_pack_stock_loc_id)
        self.assertEqual(delivery_from_wh_1.state, "waiting")
        self.assertEqual(pick_in_wh_1.move_dest_ids, delivery_from_wh_1)
        self.assertEqual(delivery_from_wh_1.picking_type_id.code, "outgoing")
        self.assertEqual(delivery_from_wh_1.picking_type_id, self.wh_1.out_type_id)
        self.assertEqual(
            delivery_from_wh_1.location_id, self.wh_1.wh_output_stock_loc_id
        )
        self.assertEqual(delivery_from_wh_1.location_dest_id.usage, "transit")
        # Validating the first move to process second one.
        self.assertEqual(delivery_from_wh_1.move_dest_ids, receipt_at_wh_2)
        self.assertEqual(receipt_at_wh_2.state, "waiting")
        self.assertEqual(receipt_at_wh_2.picking_type_id, self.wh_2.in_type_id)
        self.assertEqual(
            delivery_from_wh_1.location_dest_id, receipt_at_wh_2.location_id
        )

    def test_05_recreate_routes_assignation(self):
        """Test that the resupply routes are correctly assigned after
        recreating new ones."""
        wh_3 = self.env["stock.warehouse"].create({"name": "Test WH 3", "code": "WH3"})
        wh_4 = self.env["stock.warehouse"].create(
            {
                "name": "Test WH 4",
                "code": "WH4",
                "resupply_wh_ids": [(6, 0, [self.wh_1.id, self.wh_2.id, wh_3.id])],
            }
        )

        wh_4_old_routes = wh_4.resupply_route_ids
        self.assertEqual(len(wh_4_old_routes), 3)
        r_wh_1_to_wh4 = wh_4_old_routes.filtered(lambda r: "WH 1" in r.name)
        self.assertEqual(len(r_wh_1_to_wh4), 1)
        r_wh_2_to_wh4 = wh_4_old_routes.filtered(lambda r: "WH 2" in r.name)
        self.assertEqual(len(r_wh_2_to_wh4), 1)
        r_wh_3_to_wh4 = wh_4_old_routes.filtered(lambda r: "WH 3" in r.name)
        self.assertEqual(len(r_wh_3_to_wh4), 1)
        # Assign one route for a product, a product category and a warehouse.
        self.product.route_ids += r_wh_1_to_wh4
        self.category.route_ids = r_wh_2_to_wh4
        wh_4.route_ids += r_wh_3_to_wh4
        # Change to push and recreate routes:
        wh_4.write({"resupply_wh_push": True})
        wh_4.action_recreate_resupply_routes()
        self.assertTrue(all(not r.active for r in wh_4_old_routes))
        new_resupply_route = wh_4.resupply_route_ids
        self.assertEqual(len(new_resupply_route), 3)
        new_wh_1_to_wh4 = new_resupply_route.filtered(lambda r: "WH 1" in r.name)
        self.assertEqual(len(new_wh_1_to_wh4), 1)
        new_wh_2_to_wh4 = new_resupply_route.filtered(lambda r: "WH 2" in r.name)
        self.assertEqual(len(new_wh_2_to_wh4), 1)
        new_wh_3_to_wh4 = new_resupply_route.filtered(lambda r: "WH 3" in r.name)
        self.assertEqual(len(new_wh_3_to_wh4), 1)
        # Check reassignment of routes:
        self.assertIn(new_wh_1_to_wh4, self.product.route_ids)
        self.assertIn(new_wh_2_to_wh4, self.category.route_ids)
        self.assertIn(new_wh_3_to_wh4, wh_4.route_ids)

    def test_06_enable_push_from_preexisting_wh(self):
        """Test that enabling resupply push from an existing warehouse
        creates picking types needed and succeeds creating routes."""
        self.assertFalse(self.wh_0.out_inter_wh_internal_type_id)
        self.assertFalse(self.wh_0.out_inter_wh_external_type_id)
        self.wh_1.write(
            {
                "resupply_wh_ids": [(6, 0, [self.wh_0.id])],
            }
        )
        self.wh_1.invalidate_recordset()
        self.assertFalse(self.wh_0.out_inter_wh_internal_type_id)
        self.assertFalse(self.wh_0.out_inter_wh_external_type_id)
        self.wh_1.write({"resupply_wh_push": True})
        self.wh_1.action_recreate_resupply_routes()
        self.wh_1.invalidate_recordset()
        self.assertTrue(self.wh_0.out_inter_wh_internal_type_id)
        self.assertTrue(self.wh_0.out_inter_wh_external_type_id)
        r_wh_0_to_wh_1 = self.wh_1.resupply_route_ids
        self.assertEqual(len(r_wh_0_to_wh_1), 1)
        self.assertIn(
            self.wh_0.out_inter_wh_internal_type_id,
            r_wh_0_to_wh_1.mapped("rule_ids.picking_type_id"),
        )

    def test_07_apply_to_external_wh(self):
        """Test enabling resupply push from an external warehouse
        (belonging to another company)"""
        self.assertEqual(len(self.wh_2.resupply_route_ids), 1)
        route_wh_1_to_wh_2 = self.wh_2.resupply_route_ids
        self.assertIn("push", route_wh_1_to_wh_2.rule_ids.mapped("action"))
        self.wh_2.write({"resupply_wh_ids": [(4, self.wh_comp_2.id)]})
        self.assertEqual(len(self.wh_2.resupply_route_ids), 2)
        route_wh_comp_2_to_wh_2 = self.wh_2.resupply_route_ids - route_wh_1_to_wh_2
        # Not supported yet as explained in the ROADMAP so falling back to standard.
        self.assertNotIn("push", route_wh_comp_2_to_wh_2.rule_ids.mapped("action"))

    def test_08_push_rule_triggered_by_manual_picking(self):
        """Test that the push rule (with warehouse_id=False) is triggered when
        a manual inter-warehouse picking is validated, not via procurement.

        The push rule must have warehouse_id=False so it applies regardless of
        the warehouse context of the move. The correct destination warehouse is
        resolved via the push_domain, which filters by the picking's delivery
        address (partner_id) matching the destination warehouse's address.
        """
        push_rule = self.route_wh_1_to_wh_2.rule_ids.filtered(
            lambda r: r.action == "push"
        )
        self.assertFalse(push_rule.warehouse_id)
        transit_location = push_rule.location_src_id

        # Create a manual delivery picking from wh_1 to the transit location,
        # with partner_id matching wh_2 so push_domain selects the right rule.
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.wh_1.out_inter_wh_internal_type_id.id,
                "location_id": self.wh_1.lot_stock_id.id,
                "location_dest_id": transit_location.id,
                "partner_id": self.wh_2.partner_id.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 5.0,
                            "location_id": self.wh_1.lot_stock_id.id,
                            "location_dest_id": transit_location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids.write({"picked": True})
        picking._action_done()
        self.assertEqual(picking.state, "done")

        # The push rule should have created a receipt at wh_2
        receipt_move = picking.move_ids.move_dest_ids
        self.assertEqual(len(receipt_move), 1)
        self.assertEqual(receipt_move.picking_type_id, self.wh_2.in_type_id)
        self.assertEqual(receipt_move.location_id, transit_location)
        self.assertEqual(receipt_move.location_dest_id, self.wh_2.lot_stock_id)
        self.assertEqual(receipt_move.state, "assigned")

    def test_09_resupply_from_wh_push_multiple_wh_supplied(self):
        # Check pull rule has partner_address_id set from wh_5 partner_id
        pull_rule_wh5 = self.route_wh_1_to_wh_5.rule_ids.filtered(
            lambda x: x.action == "pull"
        )
        self.assertEqual(pull_rule_wh5.partner_address_id, self.wh_5.partner_id)
        # Check push rule has push_domain has partner_id from wh_5
        push_rule_wh5 = self.route_wh_1_to_wh_5.rule_ids.filtered(
            lambda x: x.action == "push"
        )
        self.assertEqual(
            push_rule_wh5.push_domain,
            "[('partner_id', '=', %d)]" % self.wh_5.partner_id.id,
        )

        moves = self._run_procurement(self.product, self.wh_2, 5)
        # We expect only the delivery from wh 1 to wh 2.
        self.assertEqual(len(moves), 1)
        delivery_from_wh_1 = moves
        self.assertEqual(delivery_from_wh_1.picking_type_id.code, "outgoing")
        self.assertEqual(
            delivery_from_wh_1.picking_type_id, self.wh_1.out_inter_wh_internal_type_id
        )
        self.assertEqual(delivery_from_wh_1.location_dest_id.usage, "transit")
        # Validating the first move create the next one
        self._validate_picking(delivery_from_wh_1.picking_id)
        self.assertEqual(delivery_from_wh_1.state, "done")
        receipt_at_wh_2 = delivery_from_wh_1.move_dest_ids
        self.assertEqual(len(receipt_at_wh_2), 1)
        self.assertEqual(receipt_at_wh_2.state, "assigned")
        self.assertEqual(receipt_at_wh_2.picking_type_id, self.wh_2.in_type_id)
        self.assertEqual(
            delivery_from_wh_1.location_dest_id, receipt_at_wh_2.location_id
        )
        self._validate_picking(receipt_at_wh_2.picking_id)
        self.assertEqual(receipt_at_wh_2.state, "done")

        moves = self._run_procurement(self.product, self.wh_5, 5)
        # We expect only the delivery from wh 1 to wh 5.
        self.assertEqual(len(moves), 1)
        delivery_from_wh_1 = moves
        self.assertEqual(delivery_from_wh_1.picking_type_id.code, "outgoing")
        self.assertEqual(
            delivery_from_wh_1.picking_type_id, self.wh_1.out_inter_wh_internal_type_id
        )
        self.assertEqual(delivery_from_wh_1.location_dest_id.usage, "transit")
        # Validating the first move create the next one
        self._validate_picking(delivery_from_wh_1.picking_id)
        self.assertEqual(delivery_from_wh_1.state, "done")
        receipt_at_wh_5 = delivery_from_wh_1.move_dest_ids
        self.assertEqual(len(receipt_at_wh_5), 1)
        self.assertEqual(receipt_at_wh_5.state, "assigned")
        self.assertEqual(receipt_at_wh_5.picking_type_id, self.wh_5.in_type_id)
        self.assertEqual(
            delivery_from_wh_1.location_dest_id, receipt_at_wh_5.location_id
        )
        self._validate_picking(receipt_at_wh_5.picking_id)
        self.assertEqual(receipt_at_wh_5.state, "done")
