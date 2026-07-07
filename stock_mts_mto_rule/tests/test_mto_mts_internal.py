# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.stock.models.stock_rule import ProcurementGroup

from .common import MtoMtsRouteCommon


class TestMtoMtsInternal(MtoMtsRouteCommon):
    """
    These are tests to implement MTO/MTS for internal replenishments flows.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a zone view to gather pickable goods and reserve ones
        cls.zone_a = cls.location_obj.create(
            {
                "name": "ZONE A",
                "location_id": cls.warehouse.lot_stock_id.id,
                "usage": "view",
            }
        )

        cls.reserve_a = cls.location_obj.create(
            {
                "name": "Reserve A",
                "location_id": cls.zone_a.id,
                "usage": "view",
            }
        )

        cls.pickable_a = cls.location_obj.create(
            {
                "name": "Pickable A",
                "location_id": cls.zone_a.id,
                "usage": "view",
            }
        )

        cls.reserve_a_1 = cls.location_obj.create(
            {
                "name": "Reserve A-1",
                "location_id": cls.reserve_a.id,
                "usage": "internal",
            }
        )
        cls.reserve_a_2 = cls.location_obj.create(
            {
                "name": "Reserve A-2",
                "location_id": cls.reserve_a.id,
                "usage": "internal",
            }
        )

        cls.pickable_a_1 = cls.location_obj.create(
            {
                "name": "Pickable A-1",
                "location_id": cls.pickable_a.id,
                "usage": "internal",
            }
        )

        cls.pickable_a_2 = cls.location_obj.create(
            {
                "name": "Pickable A-2",
                "location_id": cls.pickable_a.id,
                "usage": "internal",
            }
        )

        cls.route_reserve = cls.route_obj.create(
            {
                "name": "Reserve A -> Pickable A",
            }
        )
        cls.pick_type_reserve = cls.picking_type_obj.create(
            {
                "name": "Reserve A -> Pickable A",
                "sequence_code": "RES/",
                "default_location_src_id": cls.reserve_a.id,
                "default_location_dest_id": cls.pickable_a.id,
            }
        )
        cls.rule_mts_reserve = cls.rule_obj.create(
            {
                "name": "MTS Reserve A -> Stock",
                "action": "pull",
                "sequence": 1,
                "procure_method": "make_to_stock",
                "picking_type_id": cls.pick_type_reserve.id,
                "location_dest_id": cls.pickable_a.id,
                "location_src_id": cls.reserve_a.id,
                "route_id": cls.route_reserve.id,
            }
        )

        cls.rule_mto_reserve = cls.rule_obj.create(
            {
                "name": "MTO Reserve A -> Stock",
                "action": "pull",
                "sequence": 1,
                "procure_method": "make_to_order",
                "picking_type_id": cls.pick_type_reserve.id,
                "location_dest_id": cls.pickable_a.id,
                "location_src_id": cls.reserve_a.id,
                "route_id": cls.route_reserve.id,
            }
        )

        cls.rule_split_reserve = cls.rule_obj.create(
            {
                "name": "Split Reserve A -> Stock",
                "action": "split_procurement",
                "sequence": 0,
                "picking_type_id": cls.pick_type_reserve.id,
                "location_dest_id": cls.pickable_a.id,
                "location_src_id": cls.reserve_a.id,
                "mto_rule_id": cls.rule_mto_reserve.id,
                "mts_rule_id": cls.rule_mts_reserve.id,
                "route_id": cls.route_reserve.id,
            }
        )

        cls.product_1 = cls.product.create(
            {
                "name": "Product 1",
                "is_storable": True,
            }
        )
        # Create quantity in Reserve for product 1
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "inventory_quantity": 100.0,
                "product_id": cls.product_1.id,
                "location_id": cls.reserve_a_1.id,
            }
        )._apply_inventory()

    def test_mto_mts(self):
        """
        Create two needs on Pickable stock location of 75.0 each

        One move of 75.0 is created from Reserve -> Pickable
        One move of 25.0 is created from Reserve -> Pickable
        One move of 50.0 is created from Reserve -> Pickable
        One move of 50.0 is created from Suppliers -> Reserve
        """
        self.group_1 = self.env["procurement.group"].create({"name": "Group 1"})
        self.group_2 = self.env["procurement.group"].create({"name": "Group 2"})
        values_1 = {"route_ids": self.route_reserve, "group_id": self.group_1}
        values_2 = {"route_ids": self.route_reserve, "group_id": self.group_2}
        procurements = [
            ProcurementGroup.Procurement(
                self.product_1,
                75.0,
                self.product_1.uom_id,
                self.pickable_a,
                "Test",
                "Test",
                self.warehouse.company_id,
                values_1,
            ),
            ProcurementGroup.Procurement(
                self.product_1,
                75.0,
                self.product_1.uom_id,
                self.pickable_a,
                "Test",
                "Test",
                self.warehouse.company_id,
                values_2,
            ),
        ]

        self.env["procurement.group"].run(procurements)

        moves = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product_1.id),
                ("location_dest_id", "=", self.pickable_a.id),
            ]
        )
        self.assertEqual(len(moves), 3)
        moves_assigned = moves.filtered(lambda m: m.state == "assigned")
        sum_qty = 0
        for move in moves_assigned:
            sum_qty += move.quantity
            self.assertEqual(move.location_dest_id, self.pickable_a)
        self.assertEqual(100.0, sum_qty)
        moves_waiting = moves.filtered(lambda m: m.state == "waiting")
        self.assertEqual(moves_waiting.product_uom_qty, 50.0)
        self.assertEqual(
            moves_waiting.move_orig_ids.location_id,
            self.env.ref("stock.stock_location_suppliers"),
        )
