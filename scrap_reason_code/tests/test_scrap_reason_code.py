# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class StockScrap(TransactionCase):
    def setUp(self):
        super(StockScrap, self).setUp()

        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        stock_location_locations_virtual = self.env["stock.location"].create(
            {"name": "Virtual Locations", "usage": "view", "posz": 1}
        )
        self.scrapped_location = self.env["stock.location"].create(
            {
                "name": "Scrapped",
                "location_id": stock_location_locations_virtual.id,
                "scrap_location": True,
                "usage": "inventory",
            }
        )

        self.scrap_product = self.env["product.product"].create(
            {
                "name": "Scrap Product A",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )

        self.reason_code = self.env["scrap.reason.code"].create(
            {
                "name": "DM300",
                "description": "Product is damage",
                "location_id": self.scrapped_location.id,
            }
        )

        self.uom_unit = self.env.ref("uom.product_uom_unit")

    def test_scrap_reason_code(self):
        """Scrap the product of a picking. Then modify the
        done linked stock move and ensure the scrap quantity is also
        updated and verify scrap reason code
        """
        self.env["stock.quant"]._update_available_quantity(
            self.scrap_product, self.stock_location, 10
        )
        partner = self.env["res.partner"].create({"name": "BOdedra"})
        picking = self.env["stock.picking"].create(
            {
                "name": "A single picking with one move to scrap",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        move1 = self.env["stock.move"].create(
            {
                "name": "A move to confirm and scrap its product",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": self.scrap_product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 1.0,
                "picking_id": picking.id,
            }
        )
        move1._action_confirm()

        self.assertEqual(move1.state, "confirmed")
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.scrap_product.id,
                "product_uom_id": self.scrap_product.uom_id.id,
                "scrap_qty": 5,
                "picking_id": picking.id,
                "reason_code_id": self.reason_code.id,
            }
        )
        scrap._onchange_reason_code_id()
        scrap.do_scrap()
        self.assertEqual(len(picking.move_lines), 2)
        scrapped_move = picking.move_lines.filtered(lambda m: m.state == "done")
        self.assertTrue(scrapped_move, "No scrapped move created.")
        self.assertEqual(
            scrapped_move.scrap_ids.ids, [scrap.id], "Wrong scrap linked to the move."
        )
        self.assertEqual(
            scrap.scrap_qty,
            5,
            "Scrap quantity has been modified and is not " "correct anymore.",
        )
        move = scrap.move_id
        self.assertEqual(move.reason_code_id.id, self.reason_code.id)

        scrapped_move.quantity_done = 8
        self.assertEqual(scrap.scrap_qty, 8, "Scrap quantity is not updated.")
