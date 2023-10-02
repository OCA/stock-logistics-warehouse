# Copyright 2023 ForgeFLow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestStockReserveArea(common.TransactionCase):
    def setUp(self):
        """
        We will create 4 reserve areas:
        - Company level reserve area
            - WH1 Reserve Area
                - WH1-Stock1 Reserve Area
            - WH2 Reserve Area

        """
        super().setUp()
        self.warehouse1 = self.env["stock.warehouse"].create(
            {"name": "Test warehouse 1", "code": "TWH1"}
        )
        self.warehouse2 = self.env["stock.warehouse"].create(
            {"name": "Test warehouse 2", "code": "TWH2"}
        )
        self.wh1_stock1 = self.warehouse1.lot_stock_id
        self.wh1_stock2 = self.env["stock.location"].create(
            {
                "name": "Stock2",
                "location_id": self.warehouse1.view_location_id.id,
            }
        )
        self.wh2_stock1 = self.warehouse2.lot_stock_id
        self.customer_location = self.env.ref("stock.stock_location_customers")

        self.product = self.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )

        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.wh1_stock1.id,
                "quantity": 10.0,
            }
        )

        self.reserve_area1 = self.env["stock.reserve.area"].search(
            [("location_ids", "in", self.warehouse1.view_location_id.id)]
        )

        # when creating the warehouse, its reserve area has been created automatically
        # but Stock2 location wasn't created yet
        self.reserve_area1.location_ids += self.wh1_stock2

        self.reserve_area2 = self.env["stock.reserve.area"].search(
            [("location_ids", "in", self.warehouse2.view_location_id.id)]
        )

        self.stock_reserve_area_wh1_stck1 = self.env["stock.reserve.area"].create(
            {
                "name": "WH1-Stock1",
                "location_ids": [(6, 0, [self.wh1_stock1.id])],
                "company_id": self.env.user.company_id.id,
            }
        )

        all_locations = (
            self.reserve_area1.location_ids + self.reserve_area2.location_ids
        )

        self.reserve_area_company = self.env["stock.reserve.area"].create(
            {
                "name": "Company",
                "location_ids": [(6, 0, all_locations.ids)],
                "company_id": self.env.user.company_id.id,
            }
        )
        self.picking_type_out = self.env.ref("stock.picking_type_out")
        self.picking_type_internal = self.env.ref("stock.picking_type_internal")

    def test_reservation_picking_area1(self):
        """We create a picking from WH1-Stock1 to WH1-Stock2.
        The only reserve area impacted should be WH1-Stock1 and since there is stock of
         it in the source location
        it should be reserved in the Area and locally.
        """
        picking_internal_area = self.env["stock.picking"].create(
            {
                "location_id": self.wh1_stock1.id,
                "location_dest_id": self.wh1_stock2.id,
                "picking_type_id": self.picking_type_internal.id,
                "company_id": self.env.company.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_internal_area.id,
                "location_id": self.wh1_stock1.id,
                "location_dest_id": self.wh1_stock2.id,
            }
        )
        picking_internal_area.action_confirm()
        picking_internal_area.action_assign()
        self.assertEqual(len(move.reserve_area_line_ids), 1)
        self.assertEqual(move.reserve_area_line_ids.reserve_area_id.name, "WH1-Stock1")
        self.assertEqual(
            move.reserve_area_line_ids.reserved_availability,
            1,
            "1 unit should have been "
            "reserved in the WH1-Stock1 Reserve Area"
            "for this product.",
        )
        self.assertEqual(
            move.area_reserved_availability,
            1,
            "1 units should have been "
            "reserved in the move for all Areas"
            "for this product.",
        )
        self.assertEqual(
            move.reserved_availability,
            1,
            "1 units should have been "
            "reserved in the source location move"
            "for this product.",
        )

    def test_reservation_picking_out_area2(self):
        """We create a picking where the product will go out of all reserve areas except
         WH2.
        There is stock of it in the source location.
        The product should be reserved in all impacted areas and in the location."""
        picking_out_area = self.env["stock.picking"].create(
            {
                "location_id": self.wh1_stock1.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
                "company_id": self.env.company.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_out_area.id,
                "location_id": self.wh1_stock1.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking_out_area.action_confirm()
        picking_out_area.action_assign()
        self.assertEqual(len(move.reserve_area_line_ids), 3)
        self.assertEqual(
            move.area_reserved_availability,
            1,
            "One unit should have been "
            "reserved in all Reserve Areas"
            "for this product.",
        )
        self.assertEqual(
            move.reserved_availability,
            1,
            "One unit should have been " "reserved for this product in TWH1/Stock.",
        )
        for sml in picking_out_area.move_lines.mapped("move_line_ids"):
            sml.qty_done = sml.product_qty
        picking_out_area._action_done()
        self.assertEqual(
            move.area_reserved_availability,
            0,
            "There shouldn't be any reserved units in the area for this move.",
        )

    def test_reservation_picking_out_area3(self):
        """We create a picking where the product will go out of WH2 and Company reserve
         areas.
        There is no stock of it in the source location.
        The product should be reserved only in the Company area but not in the others or
         in the source location."""
        picking_out_area = self.env["stock.picking"].create(
            {
                "location_id": self.wh2_stock1.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
                "company_id": self.env.company.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_out_area.id,
                "location_id": self.wh2_stock1.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking_out_area.action_confirm()
        picking_out_area.action_assign()
        self.assertEqual(len(move.reserve_area_line_ids), 2)
        self.assertEqual(
            move.area_reserved_availability,
            0,
            "0 units should have been "
            "reserved in all Reserve Areas"
            "for this product.",
        )
        self.assertEqual(
            move.reserved_availability,
            0,
            "0 units should have been reserved for this product in TWH2/Stock.",
        )
        for area_line in move.reserve_area_line_ids:
            if area_line.reserve_area_id.name == "Company":
                self.assertEqual(area_line.reserved_availability, 1)
            else:
                self.assertEqual(area_line.reserved_availability, 0)

        picking_out_area.do_unreserve()
        self.assertEqual(
            move.area_reserved_availability,
            0,
            "There shouldn't be any reserved units in the area for this move.",
        )
