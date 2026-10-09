# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestSafeInventory(BaseCommon):
    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        self.location = self.env["stock.location"].create(
            {"name": "Location", "usage": "internal"}
        )
        self.quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.location.id,
                "quantity": 10.0,
            }
        )
        self.picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.location.id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        self.move = self.env["stock.move"].create(
            {
                "name": "Move",
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.location.id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )

    @classmethod
    def _make_inventory(cls, product, location, qty):
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "inventory_quantity": qty,
            }
        )._apply_inventory()

    def test_safe_inventory_qty_done(self):
        self.picking.action_assign()
        self.picking.move_line_ids.write({"qty_done": 5.0})
        self.env.company.stock_quant_no_inventory_if_being_picked = True
        with self.assertRaisesRegex(
            UserError,
            "You cannot update the quantity of a quant that is currently being picked",
        ):
            self._make_inventory(self.product, self.location, 5.0)
        self.env.company.stock_quant_no_inventory_if_being_picked = False
        self._make_inventory(self.product, self.location, 5.0)

    def test_safe_inventory_no_qty_done(self):
        self.picking.action_assign()
        self.env.company.stock_quant_no_inventory_if_being_picked = True
        self._make_inventory(self.product, self.location, 5.0)

    def test_set_inventory_quantity_being_picked(self):
        # setting a counted quantity is allowed, only applying it is blocked
        self.picking.action_assign()
        self.picking.move_line_ids.write({"qty_done": 5.0})
        self.env.company.stock_quant_no_inventory_if_being_picked = True
        self.quant.inventory_quantity = 0.0
        self.assertTrue(self.quant.inventory_quantity_set)
        with self.assertRaisesRegex(
            UserError,
            "You cannot update the quantity of a quant that is currently being picked",
        ):
            self.quant.action_apply_inventory()

    def test_is_being_picked(self):
        self.picking.action_assign()
        self.assertFalse(self.quant.is_being_picked)
        self.picking.move_line_ids.write({"qty_done": 5.0})
        self.quant.invalidate_recordset(["is_being_picked"])
        self.assertTrue(self.quant.is_being_picked)
        action = self.quant.action_view_current_move_lines()
        self.assertEqual(
            self.env["stock.move.line"].search(action["domain"]),
            self.picking.move_line_ids,
        )
        self.picking._action_done()
        self.quant.invalidate_recordset(["is_being_picked"])
        self.assertFalse(self.quant.is_being_picked)
