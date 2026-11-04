# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.addons.base.tests.common import BaseCommon


class TestStockPickingShowLinked(BaseCommon):
    _test_user_groups = (
        "product.group_product_manager",
        "stock.group_stock_manager",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.output_location = cls.warehouse.wh_output_stock_loc_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu", "is_storable": True}
        )
        cls.pick = cls._create_picking(
            cls,
            cls.warehouse.int_type_id,
            cls.stock_location,
            cls.output_location,
        )
        cls.ship = cls._create_picking(
            cls,
            cls.warehouse.out_type_id,
            cls.output_location,
            cls.customer_location,
        )
        cls.ship.move_ids.move_orig_ids = cls.pick.move_ids

    def _create_picking(self, picking_type, location, location_dest):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
            }
        )
        self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "product_id": self.product.id,
                "product_uom_qty": 5,
                "uom_id": self.product.uom_id.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
            }
        )
        return picking

    def test_origin_picking_count(self):
        self.assertEqual(self.ship.origin_picking_count, 1)
        self.assertEqual(self.pick.origin_picking_count, 0)

    def test_action_stock_picking_origin_single(self):
        action = self.ship.action_stock_picking_origin()
        self.assertEqual(action["res_id"], self.pick.id)
        self.assertEqual(action["views"][0][1], "form")

    def test_action_stock_picking_origin_multi(self):
        other_pick = self._create_picking(
            self.warehouse.int_type_id, self.stock_location, self.output_location
        )
        self.ship.move_ids.move_orig_ids |= other_pick.move_ids
        self.assertEqual(self.ship.origin_picking_count, 2)
        action = self.ship.action_stock_picking_origin()
        self.assertFalse(action["res_id"])
        self.assertEqual(
            action["domain"],
            f"[('id','in',{(self.pick | other_pick).ids})]",
        )
