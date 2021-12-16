# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# Copyright 2019-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import exceptions, fields
from odoo.tests import common


class TestReserveRule(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_delta = cls.env.ref("base.res_partner_4")
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WHTEST",
            }
        )
        cls.rule = cls.env.ref("stock_reserve_rule.stock_reserve_rule_1_demo")
        cls.rule.active = True

        cls.customer_loc = cls.env.ref("stock.stock_location_customers")

        cls.loc_zone1 = cls.env["stock.location"].create(
            {"name": "Zone1", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_zone1_bin1 = cls.env["stock.location"].create(
            {"name": "Zone1 Bin1", "location_id": cls.loc_zone1.id}
        )
        cls.loc_zone1_bin2 = cls.env["stock.location"].create(
            {"name": "Zone1 Bin2", "location_id": cls.loc_zone1.id}
        )
        cls.loc_zone2 = cls.env["stock.location"].create(
            {"name": "Zone2", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_zone2_bin1 = cls.env["stock.location"].create(
            {"name": "Zone2 Bin1", "location_id": cls.loc_zone2.id}
        )
        cls.loc_zone2_bin2 = cls.env["stock.location"].create(
            {"name": "Zone2 Bin2", "location_id": cls.loc_zone2.id}
        )
        cls.loc_zone3 = cls.env["stock.location"].create(
            {"name": "Zone3", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_zone3_bin1 = cls.env["stock.location"].create(
            {"name": "Zone3 Bin1", "location_id": cls.loc_zone3.id}
        )
        cls.loc_zone3_bin2 = cls.env["stock.location"].create(
            {"name": "Zone3 Bin2", "location_id": cls.loc_zone3.id}
        )

        cls.product1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Product 2", "type": "product"}
        )

        cls.unit = cls.env["product.packaging.type"].create(
            {"name": "Unit", "code": "UNIT", "sequence": 0}
        )
        cls.retail_box = cls.env["product.packaging.type"].create(
            {"name": "Retail Box", "code": "PACK", "sequence": 3}
        )
        cls.transport_box = cls.env["product.packaging.type"].create(
            {"name": "Transport Box", "code": "CASE", "sequence": 4}
        )
        cls.pallet = cls.env["product.packaging.type"].create(
            {"name": "Pallet", "code": "PALLET", "sequence": 5}
        )

    def _create_picking(self, wh, products=None, location_src_id=None):
        """Create picking

        Products must be a list of tuples (product, quantity).
        One stock move will be created for each tuple.
        """
        if products is None:
            products = []

        picking = self.env["stock.picking"].create(
            {
                "location_id": location_src_id or wh.lot_stock_id.id,
                "location_dest_id": wh.wh_output_stock_loc_id.id,
                "partner_id": self.partner_delta.id,
                "picking_type_id": wh.pick_type_id.id,
            }
        )

        for product, qty in products:
            self.env["stock.move"].create(
                {
                    "name": product.name,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "product_uom": product.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": location_src_id or wh.lot_stock_id.id,
                    "location_dest_id": wh.wh_output_stock_loc_id.id,
                    "state": "confirmed",
                }
            )
        return picking

    def _update_qty_in_location(self, location, product, quantity, in_date=None):
        self.env["stock.quant"]._update_available_quantity(
            product, location, quantity, in_date=in_date
        )

    def _create_rule(self, rule_values, removal_values):
        rule_config = {
            "name": "Test Rule",
            "location_id": self.wh.lot_stock_id.id,
            "rule_removal_ids": [(0, 0, values) for values in removal_values],
        }
        rule_config.update(rule_values)
        self.env["stock.reserve.rule"].create(rule_config)
        # workaround for https://github.com/odoo/odoo/pull/41900
        self.env["stock.reserve.rule"].invalidate_cache()

    def _setup_packagings(self, product, packagings):
        """Create packagings on a product
        packagings is a list [(name, qty, packaging_type)]
        """
        self.env["product.packaging"].create(
            [
                {
                    "name": name,
                    "qty": qty,
                    "product_id": product.id,
                    "packaging_type_id": packaging_type.id,
                }
                for name, qty, packaging_type in packagings
            ]
        )

    def test_removal_rule_location_child_of_rule_location(self):
        # removal rule location is a child
        self._create_rule({}, [{"location_id": self.loc_zone1.id}])
        # removal rule location is not a child
        with self.assertRaises(exceptions.ValidationError):
            self._create_rule(
                {}, [{"location_id": self.env.ref("stock.stock_location_locations").id}]
            )

    def test_rule_take_all_in_2(self):
        all_locs = (
            self.loc_zone1_bin1,
            self.loc_zone1_bin2,
            self.loc_zone2_bin1,
            self.loc_zone2_bin2,
            self.loc_zone3_bin1,
            self.loc_zone3_bin2,
        )
        for loc in all_locs:
            self._update_qty_in_location(loc, self.product1, 100)

        picking = self._create_picking(self.wh, [(self.product1, 200)])

        self._create_rule(
            {},
            [
                {"location_id": self.loc_zone1.id, "sequence": 2},
                {"location_id": self.loc_zone2.id, "sequence": 1},
                {"location_id": self.loc_zone3.id, "sequence": 3},
            ],
        )

        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 100},
                {"location_id": self.loc_zone2_bin2.id, "product_qty": 100},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_match_parent(self):
        all_locs = (
            self.loc_zone1_bin1,
            self.loc_zone1_bin2,
            self.loc_zone2_bin1,
            self.loc_zone2_bin2,
            self.loc_zone3_bin1,
            self.loc_zone3_bin2,
        )
        for loc in all_locs:
            self._update_qty_in_location(loc, self.product1, 100)

        picking = self._create_picking(
            self.wh, [(self.product1, 200)], self.loc_zone1.id
        )

        self._create_rule(
            {},
            [
                {"location_id": self.loc_zone1.id, "sequence": 2},
                {"location_id": self.loc_zone2.id, "sequence": 1},
                {"location_id": self.loc_zone3.id, "sequence": 3},
            ],
        )

        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone1_bin1.id, "product_qty": 100},
                {"location_id": self.loc_zone1_bin2.id, "product_qty": 100},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_take_all_in_2_and_3(self):
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone3_bin1, self.product1, 100)
        picking = self._create_picking(self.wh, [(self.product1, 150)])

        self._create_rule(
            {},
            [
                {"location_id": self.loc_zone1.id, "sequence": 3},
                {"location_id": self.loc_zone2.id, "sequence": 1},
                {"location_id": self.loc_zone3.id, "sequence": 2},
            ],
        )

        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 100},
                {"location_id": self.loc_zone3_bin1.id, "product_qty": 50},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_remaining(self):
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone3_bin1, self.product1, 100)
        picking = self._create_picking(self.wh, [(self.product1, 400)])

        self._create_rule(
            {},
            [
                {"location_id": self.loc_zone1.id, "sequence": 3},
                {"location_id": self.loc_zone2.id, "sequence": 1},
                {"location_id": self.loc_zone3.id, "sequence": 2},
            ],
        )

        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 100},
                {"location_id": self.loc_zone3_bin1.id, "product_qty": 100},
                {"location_id": self.loc_zone1_bin1.id, "product_qty": 100},
            ],
        )
        self.assertEqual(move.state, "partially_available")
        self.assertEqual(move.reserved_availability, 300.0)

    def test_rule_domain(self):
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone3_bin1, self.product1, 100)
        picking = self._create_picking(self.wh, [(self.product1, 200)])

        domain = [("product_id", "!=", self.product1.id)]
        self._create_rule(
            {"rule_domain": domain, "sequence": 1},
            [
                # this rule should be excluded by the domain
                {"location_id": self.loc_zone1.id, "sequence": 1}
            ],
        )
        self._create_rule(
            {"sequence": 2},
            [
                {"location_id": self.loc_zone2.id, "sequence": 1},
                {"location_id": self.loc_zone3.id, "sequence": 2},
            ],
        )
        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 100},
                {"location_id": self.loc_zone3_bin1.id, "product_qty": 100},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_picking_type(self):
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone3_bin1, self.product1, 100)
        picking = self._create_picking(self.wh, [(self.product1, 200)])

        self._create_rule(
            # different picking, should be excluded
            {"picking_type_ids": [(6, 0, self.wh.int_type_id.ids)], "sequence": 1},
            [{"location_id": self.loc_zone1.id, "sequence": 1}],
        )
        self._create_rule(
            # same picking type as the move
            {"picking_type_ids": [(6, 0, self.wh.pick_type_id.ids)], "sequence": 2},
            [
                {"location_id": self.loc_zone2.id, "sequence": 1},
                {"location_id": self.loc_zone3.id, "sequence": 2},
            ],
        )
        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 100},
                {"location_id": self.loc_zone3_bin1.id, "product_qty": 100},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_quant_domain(self):
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone3_bin1, self.product1, 100)
        picking = self._create_picking(self.wh, [(self.product1, 200)])

        domain = [("quantity", ">", 200)]
        self._create_rule(
            {},
            [
                # This rule is not excluded by the domain,
                # but the quant will be as the quantity is less than 200.
                {
                    "location_id": self.loc_zone1.id,
                    "sequence": 1,
                    "quant_domain": domain,
                },
                {"location_id": self.loc_zone2.id, "sequence": 2},
                {"location_id": self.loc_zone3.id, "sequence": 3},
            ],
        )
        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 100},
                {"location_id": self.loc_zone3_bin1.id, "product_qty": 100},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_empty_bin(self):
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 300)
        self._update_qty_in_location(self.loc_zone1_bin2, self.product1, 150)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 50)
        self._update_qty_in_location(self.loc_zone3_bin1, self.product1, 100)
        picking = self._create_picking(self.wh, [(self.product1, 250)])

        self._create_rule(
            {},
            [
                # This rule should be excluded for zone1 / bin1 because the
                # bin would not be empty, but applied on zone1 / bin2.
                {
                    "location_id": self.loc_zone1.id,
                    "sequence": 1,
                    "removal_strategy": "empty_bin",
                },
                # this rule should be applied because we will empty the bin
                {
                    "location_id": self.loc_zone2.id,
                    "sequence": 2,
                    "removal_strategy": "empty_bin",
                },
                {"location_id": self.loc_zone3.id, "sequence": 3},
            ],
        )
        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids

        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone1_bin2.id, "product_qty": 150.0},
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 50.0},
                {"location_id": self.loc_zone3_bin1.id, "product_qty": 50.0},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_empty_bin_partial(self):
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 50)
        self._update_qty_in_location(self.loc_zone1_bin2, self.product1, 50)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 50)
        picking = self._create_picking(self.wh, [(self.product1, 80)])

        self._create_rule(
            {},
            [
                {
                    "location_id": self.loc_zone1.id,
                    "sequence": 1,
                    "removal_strategy": "empty_bin",
                },
                {"location_id": self.loc_zone2.id, "sequence": 2},
            ],
        )
        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids

        # We expect to take 50 in zone1/bin1 as it will empty a bin,
        # but zone1/bin2 must not be used as it would not empty it.

        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone1_bin1.id, "product_qty": 50.0},
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 30.0},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_empty_bin_fifo(self):
        self._update_qty_in_location(
            self.loc_zone1_bin1,
            self.product1,
            30,
            in_date=fields.Datetime.to_datetime("2021-01-04 12:00:00"),
        )
        self._update_qty_in_location(
            self.loc_zone1_bin2,
            self.product1,
            60,
            in_date=fields.Datetime.to_datetime("2021-01-02 12:00:00"),
        )
        self._update_qty_in_location(
            self.loc_zone2_bin1,
            self.product1,
            50,
            in_date=fields.Datetime.to_datetime("2021-01-05 12:00:00"),
        )
        picking = self._create_picking(self.wh, [(self.product1, 80)])

        self._create_rule(
            {},
            [
                {
                    "location_id": self.loc_zone1.id,
                    "sequence": 1,
                    "removal_strategy": "empty_bin",
                },
                {"location_id": self.loc_zone2.id, "sequence": 2},
            ],
        )
        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids

        # We expect to take 60 in zone1/bin2 as it will empty a bin and
        # respecting fifo, the 60 of zone2 should be taken before the 30 of
        # zone1. Then, as zone1/bin1 would not be empty, it is discarded. The
        # remaining is taken in zone2 which has no rule.
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone1_bin2.id, "product_qty": 60.0},
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 20.0},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_packaging(self):
        self._setup_packagings(
            self.product1,
            [("Pallet", 500, self.pallet), ("Retail Box", 50, self.retail_box)],
        )
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 40)
        self._update_qty_in_location(self.loc_zone1_bin2, self.product1, 510)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 60)
        self._update_qty_in_location(self.loc_zone3_bin1, self.product1, 100)
        picking = self._create_picking(self.wh, [(self.product1, 590)])

        self._create_rule(
            {},
            [
                # due to this rule and the packaging size of 500, we will
                # not use zone1/bin1, but zone1/bin2 will be used.
                {
                    "location_id": self.loc_zone1.id,
                    "sequence": 1,
                    "removal_strategy": "packaging",
                },
                # zone2/bin2 will match the second packaging size of 50
                {
                    "location_id": self.loc_zone2.id,
                    "sequence": 2,
                    "removal_strategy": "packaging",
                },
                # the rest should be taken here
                {"location_id": self.loc_zone3.id, "sequence": 3},
            ],
        )
        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone1_bin2.id, "product_qty": 500.0},
                {"location_id": self.loc_zone2_bin1.id, "product_qty": 50.0},
                {"location_id": self.loc_zone3_bin1.id, "product_qty": 40.0},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_packaging_fifo(self):
        self._setup_packagings(
            self.product1,
            [("Pallet", 500, self.pallet), ("Retail Box", 50, self.retail_box)],
        )
        self._update_qty_in_location(
            self.loc_zone1_bin1,
            self.product1,
            500,
            in_date=fields.Datetime.to_datetime("2021-01-04 12:00:00"),
        )
        self._update_qty_in_location(
            self.loc_zone1_bin2,
            self.product1,
            500,
            in_date=fields.Datetime.to_datetime("2021-01-02 12:00:00"),
        )
        self._create_rule(
            {},
            [
                {
                    "location_id": self.loc_zone1.id,
                    "sequence": 1,
                    "removal_strategy": "packaging",
                },
            ],
        )

        # take in bin2 to respect fifo
        picking = self._create_picking(self.wh, [(self.product1, 50)])
        picking.action_assign()
        self.assertRecordValues(
            picking.move_lines.move_line_ids,
            [{"location_id": self.loc_zone1_bin2.id, "product_qty": 50.0}],
        )
        picking2 = self._create_picking(self.wh, [(self.product1, 50)])
        picking2.action_assign()
        self.assertRecordValues(
            picking2.move_lines.move_line_ids,
            [{"location_id": self.loc_zone1_bin2.id, "product_qty": 50.0}],
        )

    def test_rule_packaging_0_packaging(self):
        # a packaging mistakenly created with a 0 qty should be ignored,
        # not make the reservation fail
        self._setup_packagings(
            self.product1,
            [
                ("Pallet", 500, self.pallet),
                ("Retail Box", 50, self.retail_box),
                ("DivisionByZero", 0, self.unit),
            ],
        )
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 40)
        picking = self._create_picking(self.wh, [(self.product1, 590)])
        self._create_rule(
            {},
            [
                {
                    "location_id": self.loc_zone1.id,
                    "sequence": 1,
                    "removal_strategy": "packaging",
                }
            ],
        )
        # Here, it will try to reserve a pallet of 500, then an outer box of
        # 50, then should ignore the one with 0 not to fail because of division
        # by zero
        picking.action_assign()

    def test_rule_packaging_type(self):
        # only take one kind of packaging
        self._setup_packagings(
            self.product1,
            [
                ("Pallet", 500, self.pallet),
                ("Transport Box", 50, self.transport_box),
                ("Retail Box", 10, self.retail_box),
                ("Unit", 1, self.unit),
            ],
        )
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 40)
        self._update_qty_in_location(self.loc_zone1_bin2, self.product1, 600)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 30)
        self._update_qty_in_location(self.loc_zone2_bin2, self.product1, 500)
        self._update_qty_in_location(self.loc_zone3_bin1, self.product1, 500)
        picking = self._create_picking(self.wh, [(self.product1, 560)])

        self._create_rule(
            {},
            [
                # we'll take one pallet (500) from zone1/bin2, but as we filter
                # on pallets only, we won't take the 600 out of it (if the rule
                # had no type, we would have taken 100 of transport boxes).
                {
                    "location_id": self.loc_zone1.id,
                    "sequence": 1,
                    "removal_strategy": "packaging",
                    "packaging_type_ids": [(6, 0, self.pallet.ids)],
                },
                # zone2/bin2 will match the second packaging size of 50,
                # but won't take 60 because it doesn't take retail boxes
                {
                    "location_id": self.loc_zone2.id,
                    "sequence": 2,
                    "removal_strategy": "packaging",
                    "packaging_type_ids": [(6, 0, self.transport_box.ids)],
                },
                # the rest should be taken here
                {"location_id": self.loc_zone3.id, "sequence": 3},
            ],
        )
        picking.action_assign()
        move = picking.move_lines
        ml = move.move_line_ids
        self.assertRecordValues(
            ml,
            [
                {"location_id": self.loc_zone1_bin2.id, "product_qty": 500.0},
                {"location_id": self.loc_zone2_bin2.id, "product_qty": 50.0},
                {"location_id": self.loc_zone3_bin1.id, "product_qty": 10.0},
            ],
        )
        self.assertEqual(move.state, "assigned")

    def test_rule_excluded_not_child_location(self):
        self._update_qty_in_location(self.loc_zone1_bin1, self.product1, 100)
        self._update_qty_in_location(self.loc_zone1_bin2, self.product1, 100)
        self._update_qty_in_location(self.loc_zone2_bin1, self.product1, 100)
        picking = self._create_picking(self.wh, [(self.product1, 80)])

        self._create_rule(
            {},
            [
                {"location_id": self.loc_zone1.id, "sequence": 1},
                {"location_id": self.loc_zone2.id, "sequence": 2},
            ],
        )
        move = picking.move_lines

        move.location_id = self.loc_zone2
        picking.action_assign()
        ml = move.move_line_ids

        # As the source location of the stock.move is loc_zone2, we should
        # never take any quantity in zone1.

        self.assertRecordValues(
            ml, [{"location_id": self.loc_zone2_bin1.id, "product_qty": 80.0}]
        )
        self.assertEqual(move.state, "assigned")
