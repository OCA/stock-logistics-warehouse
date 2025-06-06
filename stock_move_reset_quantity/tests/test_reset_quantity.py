# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestResetQuantity(BaseCommon):
    def test_reset_quantity(self):
        picking = Form(
            self.env["stock.picking"].with_context(
                default_picking_type_id=self.ref("stock.picking_type_in")
            )
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Product Reset Quantity",
                "is_storable": True,
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        with picking.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 2.0
        picking = picking.save()
        picking.action_assign()
        self.assertEqual(picking.move_ids.quantity, 2.0)
        picking.action_reset_quantity()
        self.assertEqual(picking.move_ids.quantity, 0.0)
