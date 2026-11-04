# Copyright 2026 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestStockQuantReservationInfo(BaseCommon):
    _test_user_groups = (
        "product.group_product_manager",
        "stock.group_stock_manager",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu", "is_storable": True}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 30
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "picking_id": cls.picking.id,
                "product_id": cls.product.id,
                "product_uom_qty": 7,
                "uom_id": cls.product.uom_id.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.quant = cls.env["stock.quant"].search(
            [
                ("product_id", "=", cls.product.id),
                ("location_id", "=", cls.stock_location.id),
            ]
        )

    def test_quant_is_reserved(self):
        self.assertEqual(self.quant.reserved_quantity, 7)

    def test_action_reserved_moves(self):
        action = self.quant.action_reserved_moves()
        self.assertEqual(action["res_model"], "stock.move.line")
        self.assertIn(self.product.name, action["name"])
        move_lines = self.env["stock.move.line"].search(action["domain"])
        self.assertEqual(move_lines, self.picking.move_line_ids)

    def test_action_view_picking_from_reserved(self):
        move_line = self.picking.move_line_ids
        action = move_line.action_view_picking_from_reserved()
        self.assertEqual(action["res_model"], "stock.picking")
        self.assertEqual(action["res_id"], self.picking.id)
        self.assertEqual(
            action["views"], [(self.env.ref("stock.view_picking_form").id, "form")]
        )
