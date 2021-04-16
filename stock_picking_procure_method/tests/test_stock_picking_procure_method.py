# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockPickingMTO(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingMTO, cls).setUpClass()
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test MTO Product",
                "route_ids": [(6, 0, cls.mto_route.ids)],
                "type": "product",
            }
        )
        cls.wh_obj = cls.env["stock.warehouse"]
        cls.wh1 = cls.wh_obj.create({"name": "Test WH1", "code": "TSWH1"})
        cls.wh2 = cls.wh_obj.create(
            {
                "name": "Test WH2",
                "code": "TSWH2",
                "resupply_wh_ids": [(6, 0, cls.wh1.ids)],
            }
        )
        cls.procurement_rule = cls.env["stock.rule"].create(
            {
                "name": "TST-WH1 -> TST-WH2 MTO",
                "route_id": cls.mto_route.id,
                "action": "pull",
                "location_src_id": cls.wh1.lot_stock_id.id,
                "procure_method": "make_to_stock",
                "picking_type_id": cls.wh1.int_type_id.id,
                "location_id": cls.wh2.lot_stock_id.id,
                "warehouse_id": cls.wh2.id,
                "group_propagation_option": "propagate",
                "propagate_cancel": True,
                "propagate_warehouse_id": cls.wh1.id,
            }
        )
        cls.picking_obj = cls.env["stock.picking"].with_context(planned_picking=True)
        cls.picking = cls.picking_obj.create(
            {
                "picking_type_id": cls.wh1.int_type_id.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.wh2.lot_stock_id.id,
            }
        )

    def test_compute_procure_method(self):
        # No moves
        self.assertFalse(self.picking.procure_method)
        # A new move defaults to MTS
        move_line = self.env["stock.move"].create(
            {
                "name": "TSTMOVE001",
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 100,
                "location_id": self.wh1.lot_stock_id.id,
                "location_dest_id": self.wh2.lot_stock_id.id,
            }
        )
        self.assertEqual(self.picking.procure_method, "make_to_stock")
        # Change move procure method to MTO
        move_line.procure_method = "make_to_order"
        self.assertEqual(self.picking.procure_method, "make_to_order")
        # Add a new line with MTS rule
        move_line.copy({"procure_method": "make_to_stock"})
        self.assertFalse(self.picking.procure_method)
        # We set the procure method in the picking
        self.picking.procure_method = "make_to_order"
        self.assertEqual(self.picking.move_lines[1].procure_method, "make_to_order")
