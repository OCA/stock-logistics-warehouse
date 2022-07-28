# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockInventoryLocationState(TransactionCase):
    def setUp(self):
        super(TestStockInventoryLocationState, self).setUp()
        wh = self.env.ref("stock.warehouse0")
        self.location = wh.lot_stock_id
        childs = self.env["stock.location"].search(
            [("id", "child_of", self.location.id), ("child_ids", "=", False)]
        )
        self.child_loc_1 = childs[0]
        self.child_loc_2 = childs[1]
        self.product = self.env["product.product"].create(
            {"name": "Test", "type": "product"}
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.child_loc_1, 1
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.child_loc_2, 1
        )

        self.move = self.env["stock.move"].create(
            {
                "name": self.product.display_name,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "location_id": self.location.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "warehouse_id": wh.id,
                "picking_type_id": wh.out_type_id.id,
                "procure_method": "make_to_stock",
                "state": "draft",
            }
        )
        self.move._action_confirm()
        self.move._action_assign()

    def test_post_inventory(self):
        inventory = self.env["stock.inventory"].create(
            {
                "location_ids": [(6, 0, self.location.ids)],
                "prefill_counted_quantity": "counted",
            }
        )
        inventory.action_start()
        self.assertEqual(self.move.state, "assigned")
        loc = self.move.move_line_ids.location_id
        line_1 = inventory.line_ids.filtered(
            lambda l: l.product_id == self.product and l.location_id == loc
        )
        line_1.product_qty = 0
        inventory.action_validate()
        self.assertEqual(self.move.state, "assigned")
        self.assertNotEqual(loc, self.move.move_line_ids.location_id)
